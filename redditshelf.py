#! /bin/python

import os, sys, getopt, json, string
from pathlib import Path
from datetime import date

# License: CC-BY-NC 4.0
# Author:  Alexander Phi. Goetz


config=Path("./redditshelf.json")

def help():
    """
    Just displays help
    """

    message =
        """
        redditshelf [options]
        ====================
        Fetch your favorite redditserials.
        Requires 'reddit2epub'

        -h              Show this help
        -l              List Reddit stories
        -u              Update the shelf
        -a <address>    Adds link to known stories
            -t TITLE        Set TITLE
            -o FILE         Set file destination
        -O FOLDER       Set destination Folder
        -d TITLE        Deletes TITLE from known stories
        """
    print(help)

def list_stories():
    """
    Shows a list of all tracked stories
    """

    with open(config) as json_file:
        stories = json.load(json_file)["stories"]
        count   = len(stories)
        out     = "[{}] \"{}\" - {}"
        header  =
        """
        |||||||\\   shelf   /|||||||
        ---------------------------
        Last update: {}
        ---------------------------
        """

        # IDEA: Use the below shelf instead of the above
        shelf   =
        """
                      .--.                   .---.
                  .---|__|           .-.     |~~~|
               .--|===|--|_          |_|     |~~~|--.
               |  |===|  |'\     .---!~|  .--|   |--|
               |%%|   |  |.'\    |===| |--|%%|   |  |
               |%%|   |  |\.'\   |   | |__|  |   |  |
               |  |   |  | \  \  |===| |==|  |   |  |
               |  |   |__|  \.'\ |   |_|__|  |~~~|__|
               |  |===|--|   \.'\|===|~|--|%%|~~~|--|
               ^--^---'--^    `-'`---^-^--^--^---'--' hjw
        """

        print(header.format(json.load(json_file)["last-update"]))

        for i in range(0,count):
            print(out.format(i, stories[i]["title"], stories[i]["file"]))

def update_stories():
    """
    Updates the epub files of tracked stories
    """

    with open(config) as json_file:
        data = json.load(json_file)

        for i in range(0,len(data["stories"])):
            reddit  = data["stories"][i]["reddit"]
            file    = data["stories"][i]["file"]
            os.system("reddit2epub -i {} -o {}".format(reddit, file))

        data["last-update"] = date.today().isoformat()
        json.dump(data, json_file)

def set_folder(folder):
    """
    Sets the folder where the Stories should be saved to

    Parameter:
    folder (String):    The folder
    """

    if Path(folder).is_dir():
        with open(config, "w+") as json_file:
            cfg = json.load(json_file)
            cfg["destination-folder"] = folder
            json.dump(cfg, json_file)

    else
        print("No such folder")
        sys.exit(2)

def add_story(**kwargs):
    """
    Adds a Reddit Story to the shelf

    Parameters:
    link (String):      The link to any Reddit Story's Chapter
    title (String):     The title you would like to store it in your redditshelf
    address (String):   The address where the actual file is saved to
    """

    link     = kwargs.get('link', None)
    title    = kwargs.get('title', None)
    address  = kwargs.get('address', None)

    template =
        """
        {
            "title": {},
            "reddit": {},
            "file": {}
        }
        """

    with open(config, "w+") as json_file:
        data = json.load(json_file)

        if not link:
            print("No redditlink given")
            sys.exit(2)

        if not title:
            title = string.capwords(Path(link).stem.replace("_"," "))

        if not address:
            dest_folder = Path(data["destination_folder"])
            address = dest_folder / title.replace(" ","_").lower() / ".epub"
            # TODO: Remove prohibited chars from title

        data["stories"].append(template.format(title,link,address))
        json.dump(data, json_file)

    os.system('reddit2epub -i {} -o {}'.format(link,address))

def delete_story(story):
    """
    Deletes a Story from your shelf

    Parameters:
    story (Int|String): Identifier of the Json Object
    """

    with open(config, "w+") as json_file:
        data = json.load(json_file)

        if story.isnumeric() and int(story) < len(data["stories"]):
            file = Path(data["stories"][int(story)]["file"])
            os.system('rm {}'.format(file))
            del data["stories"][int(story)]

        elif not story.isnumeric():
            key = None

            for i in range(0,len(data["stories"])):
                if data["stories"][i]["title"] == story:
                    key = i
                    os.system("rm {}".format(data["stories"][i]["file"]))
                    break

            if key:
                del data["stories"][key]

        else
            print("Not a valid index or title not found")
            sys.exit(2)
        json.dump(data, json_file)


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hla:t:d:o:")
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()

        elif opt == '-l' and config.exists():
            list_stories()
            sys.exit()

        elif opt == '-u' and config.exists():
            update_stories()
            sys.exit()

        elif opt == '-a' and config.exits():
            if '-t' in opts or '-o' in opts:
                title = None
                dest  = None
                for opt2, arg2 in opts:
                    if opt == '-t':
                        title = arg2
                    elif opt == '-o':
                        dest = arg2
                add_story(link=arg, title=title, address=dest)
            else
                add_story(link=arg)
            sys.exit()

        elif opt == '-O' and config.exists():
            set_folder(arg)
            sys.exit()

        elif opt == '-d' and config.exists():
            delete_story(arg)
            sys.exit()
        else
            print("No config file found")
            sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
