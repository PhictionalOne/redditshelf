#! /bin/python

import json
import os
import string
import sys
from datetime import date
from pathlib import Path
import click
from ebooklib import epub
from reddit2epub.reddit2epubLib import get_chapters_from_anchor, create_book_from_chapters

# License: GNU General Public License v3 (GPLv3)
# Author:  Alexander Phi. Goetz

config = Path.home() / '.config' / 'redditshelf.json'


def check_config():
    if not config.exists():
        print("""
FATAL: No config file found!

To Set a config file use
    `redditshelf init`
""")
        sys.exit(2)


def create_book(input_url: str,
                title: str,
                output_filename: str,
                overlap: int = 2,
                all_reddit: bool = False):
    """
    Modified code copied from the reddit2epub CLI code.

    https://github.com/mircohaug/reddit2epub/blob/master/reddit2epub/reddit2epubCli.py
    """

    author, selected_submissions, search_title = get_chapters_from_anchor(input_url, overlap, all_reddit)

    len_subs = len(selected_submissions)
    print("Total number of found posts with title prefix '{}' in subreddit: {}".format(search_title, len_subs))

    if len_subs == 1:
        raise Exception("No other chapters found, which share the first {} words with other posts from this "
                        "author in this subreddit.".format(overlap))
    elif len_subs == 0:
        raise Exception("No text chapters found")
    elif len_subs >= 200:
        print("Got more than 200 submissions from author in this subreddit :-O. "
              "It may be possible that old chapters are not included.",
              file=sys.stderr)

    # set metadata
    book_id = selected_submissions[-1].id
    book_title = title
    book_author = author.name

    # Build the ebook
    book = create_book_from_chapters(book_author, book_id, book_title, reversed(selected_submissions))

    # write to the file
    epub.write_epub(output_filename, book, {})


@click.group(help='Redditshelf organizes your favorite stories and updates them')
def cli():
    pass


@cli.command(short_help='Creates Config file',
             help='Creates config file and sets up environment')
@click.option('--force', '-f', is_flag=True, default=False, required=False,
              help='Overwrite existing config file')
def init(force):
    template = '''
{
    "author": "Alexander Phi. Goetz",
    "custom-config": "~",
    "destination-folder": "~/cloud-phi/Books/",
    "last-update": "2020-04-04",
    "license": "CC-BY-NC 4.0",
    "stories": [
        {
            "file": "~/the_galactic_archives_present_humanity.epub",
            "reddit": "https://www.reddit.com/r/HFY/comments/flb50l/the_galactic_archives_present_humanity/",
            "title": "The Galactic Archives Present Humanity"
        }
    ]
}
'''
    if config.exists() and not force:
        print('Config file already exists\nNothings changed')
        sys.exit()

    else:
        with open(config, 'w+') as json_file:
            json.dump(json.loads(template), json_file, indent=4, sort_keys=True)
        print('Shelf initialized')


@cli.command(name='list',
             short_help='Lists stories',
             help='Shows a list of all tracked stories')
def list_stories():
    """
    Shows a list of all tracked stories
    """
    check_config()

    with open(config) as json_file:
        cfg = json.load(json_file)
        stories = cfg["stories"]
        count = len(stories)
        out = '[{}] "{}" \n\t> {}'
        header = """
,_, ,_, ,_, ,_, ,_,                ,_, ,_, ,_, ,_, ,_, 
| | | | | | | | | |  Last Update:  | | | | | | | | | |
|0| |1| |2| |3| |4|   {}   |5| |6| |7| |8| |9|
|_| |_| |_| |_| |_|                |_| |_| |_| |_| |_|
===================[ Reddit-Shelf ]===================
        """

        print(header.format(cfg['last-update']))

        for i in range(0, count):
            print(out.format(i, stories[i]['title'], stories[i]['file']))


@cli.command(short_help='Update Shelf contents',
             help='Updates the epub files of tracked stories')
def update():
    """
    Updates the epub files of tracked stories
    """
    check_config()

    cfg = None

    with open(config) as json_file:
        cfg = json.load(json_file)

    print('Updating')
    for i in range(0, len(cfg['stories'])):
        reddit = cfg['stories'][i]['reddit']
        file = cfg['stories'][i]['file']
        title = cfg['stories'][i]['title']
        create_book(reddit, title, file)
    print('Finished')

    # Write the new Date in the config file
    with open(config, "w") as json_file:
        cfg['last-update'] = date.today().isoformat()
        json.dump(cfg, json_file, indent=4, sort_keys=True)


@cli.command(name='set-folder',
             short_help='Set destination folder',
             help='Sets the folder where the should be saved to')
@click.argument('folder')
def set_folder(folder):
    """
    Sets the default destination folder for epub files

    :param folder:  The folder to be written to
    """
    check_config()

    new_folder = Path(folder)

    if new_folder.is_dir():
        cfg = None
        with open(config) as json_file:
            cfg = json.load(json_file)
        old_folder = Path(cfg["destination-folder"])

        # Change folder for every Story with old_folder as parent directory
        for i in range(0, len(cfg["stories"])):
            current = Path(cfg["stories"][i]["file"])

            if current.parent == old_folder:
                cfg["stories"][i]["file"] = str(new_folder / current.name)

        cfg['destination-folder'] = str(new_folder)

        with open(config, 'w') as json_file:
            json.dump(cfg, json_file, indent=4, sort_keys=True)
        print(folder + " is set as new Destination")

    else:
        print('Folder not found. Make sure it is an existing folder')
        sys.exit(2)


@cli.command(short_help='Adds a new story to the shelf',
             help='Adds to a new story to the shelf and downloads it as well')
@click.argument('link', required=True)
@click.option('--title', '-t', default=None, required=False,
              help='Set a title for the story. Defaults to capitalized link name')
@click.option('--output', '-o', default=None, required=False,
              help='Set a file path where the epub should be stored')
def add(link, title, output):
    """
    Add a Story to shelf

    :param link:    Reddit link to be used
    :param title:   Title of the entry
    :param output:  File to write EPUB
    """
    check_config()

    template = '"title":"{}", "reddit":"{}", "file":"{}"'

    def sanitize(str_in):
        bad_ones = ";:|/\\!?,%*<>\"\'"
        for l in bad_ones:
            str_in = str_in.replace(l, '')
        return str_in

    data = None

    with open(config) as json_file:
        data = json.load(json_file)

    if not title:
        title = string.capwords(Path(link).stem.replace('_', ' '))

    if not output:
        dest_folder = Path(data['destination-folder'])
        output = dest_folder / (sanitize(title.replace(' ', '_').lower()) + '.epub')

    data['stories'].append(json.loads('{' + template.format(title, link, output) + '}'))
    with open(config, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)

    create_book(link, title, output)

    print(title + ' has been added')


@cli.command(short_help='Edit existing entry',
             help='Edit an existing entry using the ID or the TITLE')
@click.argument('story', required=True)
@click.option('--title', '-t', default=None, required=False,
              help='Sets a new Title')
@click.option('--dest', '-d', default=None, required=False,
              help='Sets a new file destination')
@click.option('--link', '-l', default=None, required=False,
              help='Sets a new Reddit-link')
def edit(story, title, dest, link):
    """
    Edit an existing Entry

    :param story:   Title or ID of entry
    :param title:   Title to be set
    :param dest:    Destination to be set
    :param link:    Reddit link to be set
    """
    check_config()

    if not title and not dest and not link:
        print('Nothing changed')
        sys.exit()

    data = None
    key = None
    with open(config) as json_file:
        data = json.load(json_file)

    if story.isnumeric() and int(story) < len(data['stories']):
        key = int(story)

    elif not story.isnumeric():
        for i in range(0, len(data['stories'])):
            if story == data['stories'][i]['title']:
                key = i
                break

    else:
        print('No valid ID or TITLE')
        sys.exit(2)

    if title:
        data['stories'][key]['title'] = title
        print("\"{}\"'s title is now \"{}\"".format(story, title))

    if dest:
        os.system('rm {}'.format(data['stories'][key]['file']))
        data['stories'][key]['file'] = dest
        print("\"{}\"'s file is now found at \"{}\"".format(story, dest))

    if link:
        data['stories'][key]['reddit'] = link
        print("\"{}\"'s link is now \"{}\"".format(story, link))

    create_book(data['stories'][key]['reddit'], data['stories'][key]['title'], data['stories'][key]['file'])

    with open(config, 'w') as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)

    print('Done editing. \n\nTo update please use `redditshelf.py update`')


@cli.command(short_help='Delete a story',
             help='Deletes a story from your shelf and the epub file. STORY can either be the Index or the Title')
@click.argument('story')
def delete(story):
    """
    Deletes an entry from the Shelf

    :param story:   The Title or ID of the entry
    """
    check_config()

    data = None

    with open(config) as json_file:
        data = json.load(json_file)

    if story.isnumeric() and int(story) < len(data['stories']):
        file = Path(data['stories'][int(story)]['file'])
        os.system('rm {}'.format(file))
        del data['stories'][int(story)]
        print('Story at {} has been deleted'.format(story))

    elif not story.isnumeric():
        key = None

        for i in range(0, len(data['stories'])):
            if data['stories'][i]['title'] == story:
                key = i
                os.system('rm {}'.format(data['stories'][i]['file']))
                break

        if key:
            del data['stories'][key]
            print(story + ' has been deleted')

    else:
        print('Not a valid index or title not found')
        sys.exit(2)

    with open(config, 'w') as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)
