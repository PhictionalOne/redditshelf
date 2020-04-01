# Redditshelf
A script to organize reddit serials and storys. 

Inspired by Mirco Haug's [reddit2epub](https://github.com/mircohaug/reddit2epub)

# Requirements
Have [reddit2epub](https://github.com/mircohaug/reddit2epub) installed.

# Usage

```
Usage: redditshelf.py [OPTIONS] COMMAND [ARGS]...

  Redditshelf organizes your Reddit Stories' EBooks

Options:
  --help  Show this message and exit.

Commands:
  add         Adds a new story to the shelf
  delete      Delete a story
  list        Lists stories
  set-folder  Set destination folder
  update      Update Shelf contents
```

## List shelf content
`redditshelf.py list`

```

,_, ,_, ,_, ,_, ,_,                ,_, ,_, ,_, ,_, ,_,
| | | | | | | | | |  Last Update:  | | | | | | | | | |
|1| |2| |3| |4| |5|   2020-04-01   |6| |7| |8| |9| |0|
|_| |_| |_| |_| |_|                |_| |_| |_| |_| |_|
===================[ Reddit-Shelf ]===================

[0] "The Galactic Archives Present Humanity"
        > /home/phi/Books/the_galactic_archives_present_humanity.epub
[1] "The Hero Of Station 7743 2"
        > /home/phi/Books/the_hero_of_station_7743_2.epub
[2] "Empire Among the Stars"
        > /home/phi/Books/empire_among_the_stars.epub
[3] "Guardians By Design"
        > ~/guardians.epub
```

# Roadmap
## Features
* [ ] Edit existing entries
* [ ] Specify a config file

## Other
* [ ] Refactor code 
