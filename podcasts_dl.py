#!/usr/bin/env python3

import requests
import argparse
import argcomplete
from pyPodcastParser.Podcast import Podcast
from datetime import datetime
from datetime import timedelta
from sys import argv
import os.path


def is_valid_url(url: str) -> bool:

    # check its http or https
    protocol = url.split(':')[0]
    if protocol != 'http' and protocol != 'https':
        return False

    return True


def is_date_valid(date: str) -> bool:

    try:
        datetime_date = datetime.strptime(date, '%d/%m/%y')

    except ValueError:
        return False

    return True


def date_two_weeks_ago() -> str:
    now = datetime.now()
    two_weeks = timedelta(weeks=2)

    two_weeks_ago = now - two_weeks

    return two_weeks_ago.strftime('%d/%m/%y')


def parse_args(args: argv) -> dict:

    parser = argparse.ArgumentParser(description="Powerful command line podcast downloader")
    parser.add_argument("urls"
                        , action="store"
                        , type=str
                        , nargs='*'
                        , help="the URL of the RSS feed you want to download from")

    parser.add_argument("-B"
                        , "--batch"
                        , action="store"
                        , type=str
                        , dest="file_name"
                        , default=""
                        , help="Put RSS URL's in a file to download them all at once")

    parser.add_argument("-d"
                        , "--date-from"
                        , action="store"
                        , default=date_two_weeks_ago()
                        , type=str
                        , dest="date_from"
                        , help="the oldest you want your podcasts in the format dd/mm/yy")

    parser.add_argument("-D"
                        , "--date-to"
                        , action="store"
                        , default=datetime.now().strftime('%d/%m/%y')
                        , type=str
                        , dest="date_to"
                        , help="the newest date you want your podcasts in the format dd/mm/yy")

    parser.add_argument("-F"
                        , "--force-download"
                        , action='store_true'
                        , default=False
                        , dest='force_download'
                        , help="re-download podcasts even if they already exist")

    argcomplete.autocomplete(parser)

    # is args[1:] normally but changed for testing
    return parser.parse_args(args[1:]).__dict__


def download(args: dict) -> None:

    # if batch
    if args['file_name'] != "":
        # open the file and read urls
        args['urls'] = read_batch_file(args['file_name'])
        # overwrite the urls dict with the urls from the file

    for url in args['urls']:

        # validate url
        if is_valid_url(url):
            # download content
            feed = safe_request(url)

            #put into podcast object
            podcast = Podcast(feed.content)
            message('Downloading ' + podcast.title + ' podcast from ' + args['date_from'] + ' to ' + args['date_to'])
            # for items in podcast feed
            for item in podcast.items:
                # if within date specified
                if (datetime.strptime(args['date_from'], '%d/%m/%y')
                        <= item.date_time
                        <= datetime.strptime(args['date_to'], '%d/%m/%y')):

                    # check file doesn't already exist
                    if os.path.isfile(item.title + '.mp3') and not args['force_download']:
                        message('   episode already downloaded')
                    else:
                        # download and save
                        message('   downloading episode: ' + item.title + "...")
                        file = safe_request(item.enclosure_url)
                        message('   writing to file...')
                        open(item.title + '.mp3', 'wb').write(file.content)

        else:
            message(url + ' is not a valid rss url, cannot download podcasts')


def safe_request(url: str) -> requests.api:
    try:
        return requests.get(url, allow_redirects=True)
    except requests.exceptions.RequestException:
        message("Cannot download podcasts due to Internet connection")
        exit(1)


def is_comment(line: str) -> bool:

    for char in line:
        if char == "\n":
            return True
        if char != " ":
            if char == "#":
                return True
            else:
                return False



def message(msg: str) -> None:
    print("     " + msg)


def read_batch_file(file_name: str) -> list:
    # check line doesn't have a hash at the start (means its a comment)

    batch_file = ''
    batch_list = []

    try:

        batch_file = open(file_name, 'r')

    except FileNotFoundError:
        message("Can't find that file")
        exit(1)

    for line in batch_file:
        if not is_comment(line):
            batch_list.append(line.strip('\n'))

    batch_file.close()

    return batch_list


def main():
    download(parse_args(argv))
    message("All done, enjoy your podcasts!")


if __name__ == '__main__':
    main()
