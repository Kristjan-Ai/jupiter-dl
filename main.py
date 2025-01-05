from downloader import get_jupiter_video, get_jupiter_series
from sys import argv
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script downloads single videos/movies and series episodes from jupiter.err.ee')
    parser.add_argument("jupiter_url", type=str, help="The URL of the video page")
    parser.add_argument("-p", type=str, help="Adds a string to the path in conf.py", default="")
    parser.add_argument("-c", type=str, help="Choose parts of the media to download.  Default: both", default="both", choices=("video","subs","both"))
    parser.add_argument("-m", type=str, help="Choose download mode. \"single\" downloads only the video in the URL provided. \"series\" tries to find all available episodes.   Default: single", default="single", choices=("single","series"))
    parser.add_argument("--debugging", action="store_true", help="Prints additional information", default=False)
    
    args = parser.parse_args()
    jupiter_url = args.jupiter_url
    mode = args.c
    dl_type = args.m
    path = args.p
    debug = args.debugging
    
    if dl_type == "single":
        get_jupiter_video(jupiter_url, mode, path, debug)
    elif dl_type == "series":
        print("getting episodes...")
        get_jupiter_series(jupiter_url, mode, path, debug)
