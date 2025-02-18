from conf import dl_dir
from downloader import get_jupiter_video, get_jupiter_series
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script downloads single videos/movies and series episodes from jupiter.err.ee')
    parser.add_argument("jupiter_page", type=str, help="The URL/ID of the video page")
    parser.add_argument("-s", type=str, help=f"Adds a string to the path in conf.py ({dl_dir}) or to the absolute path.", default="")
    parser.add_argument("-p", type=str, help="Absolute path of the download directory", default=dl_dir)
    parser.add_argument("-c", type=str, help="Choose parts of the media to download.  Default: both", default="both", choices=("video","subs","both"))
    parser.add_argument("-m", type=str, help="Choose download mode. \"single\" downloads only the video in the page provided. \"series\" tries to find all available episodes.   Default: single", default="single", choices=("single","series"))
    parser.add_argument("--series_folder", action="store_true", help="Creates a folder named by the series title for all the series files.", default=False)
    parser.add_argument("--debugging", action="store_true", help="Prints additional information", default=False)

    args = parser.parse_args()
    if "err.ee" not in args.jupiter_page:
        if not args.jupiter_page.isdecimal():
            parser.error(f"Check URL or video ID: {args.jupiter-dl}")
        else:
            jupiter_url = f"https://err.ee/{args.jupiter_page}"
    else:
        jupiter_url = args.jupiter_page
    parts = args.c
    mode = args.m
    path = args.p+args.s
    debug = args.debugging
    
    if mode == "single":
        get_jupiter_video(jupiter_url, parts, path, debug)
    elif mode == "series":
        get_jupiter_series(jupiter_url, parts, path, args.series_folder, debug)
