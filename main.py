from downloader import get_jupiter_video, get_jupiter_series
from sys import argv

if __name__ == "__main__":
    print("[dl, subs or both] [single/series] [jupiter url]")
    if len(argv) < 4:
        jupiter_url = input("url: ")
    else:
        jupiter_url = argv[3]
    if len(argv) < 2:
        choice = input("dl, subs or both? ")
    else:
        choice = argv[1]
    if len(argv) < 2:
        dl_type = input("series/single? ")
    else:
        dl_type = argv[2]
        
    if dl_type == "single":
        get_jupiter_video(jupiter_url, choice)
    elif dl_type == "series":
        print("getting episodes...")
        get_jupiter_series(jupiter_url, choice)
