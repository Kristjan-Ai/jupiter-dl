from conf import conf
from downloader import get_jupiter_video, get_jupiter_series
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script downloads single videos/movies and series episodes from jupiter.err.ee')
    parser.add_argument("jupiter_page", type=str, help="The URL/ID of the video page")
    parser.add_argument("-s", type=str, help=f"Adds a string to the path in conf.py ({conf["dl_dir"]}) or to the absolute path.", default="")
    parser.add_argument("-p", type=str, help="Absolute path of the download directory", default=conf["dl_dir"])
    parser.add_argument("-c", type=str, help="Choose parts of the media to download.  Default: both", default=conf["choice"], choices=("video","subs","both"))
    parser.add_argument("-m", type=str, help="Choose download mode. \"single\" downloads only the video in the page provided. \"series\" tries to find all available episodes.   Default: single", default=conf["mode"], choices=("single","series"))
    parser.add_argument("--create_folder", action="store_true", help="Creates a folder for the downloaded files.", default=conf["create_folder"])
    parser.add_argument("--debugging", action="store_true", help="Prints additional information", default=conf["debug"])
    args = parser.parse_args()
    if "err.ee" not in args.jupiter_page:
        if not args.jupiter_page.isdecimal():
            parser.error(f"Check URL or video ID: {args.jupiter_page}")
        else:
            jupiter_url = f"https://err.ee/{args.jupiter_page}"
    else:
        jupiter_url = args.jupiter_page
    parts = args.c
    mode = args.m
    path = args.p+args.s
    debug = args.debugging
    if debug: print(f"jupiter_url = {jupiter_url}\nparts = {parts}\nmode = {mode}\npath = {path}\ndebug = {debug}")
    
    if mode == "single":
        get_jupiter_video(jupiter_url, parts, path, args.create_folder, debug)
    elif mode == "series":
        get_jupiter_series(jupiter_url, parts, path, args.create_folder, debug)
