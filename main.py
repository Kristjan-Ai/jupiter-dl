from downloader import get_jupiter

if __name__ == "__main__":
    jupiter_url = input("url: ")
    print("getting master...")
    get_jupiter(jupiter_url)
