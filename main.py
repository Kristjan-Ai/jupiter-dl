from downloader import get_jupiter_video, get_jupiter_series
from sys import argv

if __name__ == "__main__":
    print("[add to dl path] [dl, subs or both] [single/series] [jupiter url]")
    if len(argv) < 2:
        jupiter_url = input("url: ")
    else:
        jupiter_url = argv[1]
    
    if len(argv) < 5:
        path = input("String to add to dl path in conf: ")
        mode = input("dl, subs or both? ")
        dl_type = input("series/single? ")
    else:
        path = argv[1]
        mode = argv[2]
        dl_type = argv[3]
        jupiter_url = argv[4]
 
    if dl_type == "single":
        get_jupiter_video(jupiter_url, mode, path)
    elif dl_type == "series":
        print("getting episodes...")
        get_jupiter_series(jupiter_url, mode, path)
