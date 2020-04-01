#! /bin/python

import json
import os
import string
import sys
from datetime import date
from pathlib import Path
import click

# License: CC-BY-NC 4.0
# Author:  Alexander Phi. Goetz

config = Path('./redditshelf.json')


@click.group()
def cli():
    if config.exists():
        pass
    else:
        print('FATAL: No config file found!')
        sys.exit(2)


@cli.command(name='list',
             short_help='Lists stories',
             help='Shows a list of all tracked stories')
def list_stories():
    """
    Shows a list of all tracked stories
    """

    with open(config) as json_file:
        cfg = json.load(json_file)
        stories = cfg["stories"]
        count = len(stories)
        out = '[{}] "{}" \n\t> {}'
        header = """
,_, ,_, ,_, ,_, ,_,                ,_, ,_, ,_, ,_, ,_, 
| | | | | | | | | |  Last Update:  | | | | | | | | | |
|1| |2| |3| |4| |5|   {}   |6| |7| |8| |9| |0|
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

    cfg = None

    with open(config) as json_file:
        cfg = json.load(json_file)

    for i in range(0, len(cfg['stories'])):
        reddit = cfg['stories'][i]['reddit']
        file = cfg['stories'][i]['file']
        os.system('reddit2epub -i {} -o {}'.format(reddit, file))

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
    Sets the folder where the Stories should be saved to

    Parameter:
    folder (String):    The folder
    """

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
    Adds a Reddit Story to the shelf

    Parameters:
    link (String):      The link to any Reddit Story's Chapter
    title (String):     The title you would like to store it in your redditshelf
    output (String):    The address where the actual file is saved to
    """

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

    os.system('reddit2epub -i {} -o {}'.format(link, output))

    print(title + ' has been added')


@cli.command(short_help='Delete a story',
             help='Deletes a story from your shelf and the epub file. STORY can either be the Index or the Title')
@click.argument('story')
def delete(story):
    """
    Deletes a Story from your shelf

    Parameters:
    story (Int|String): Identifier of the Json Object
    """

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


if __name__ == "__main__":
    cli()
