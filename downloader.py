from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
import subprocess


def get_jupiter(jupiter_url, sys_argv):
    # Create a new instance of the Firefox driver in headless mode
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(
        options=options
    )

    # Go to the Jupiter link
    driver.get(jupiter_url)
    print(f"URL = {jupiter_url}")

    # get the master m3u8
    [master] = [item.url for item in driver.requests if item.response and "master" in item.url]
    print(f"master = {master}")
    driver.quit()

    parts = jupiter_url.split("/")
    last_part = parts[-1]

    if sys_argv == "dl":
        print("DL")
        subprocess.run(
            ["yt-dlp",
             "-f", "bv*+mergeall[vcodec=none]",
             "--audio-multistreams",
             "--embed-subs",
             "--external-downloader", "aria2c",
             "--external-downloader-args", "-c -j 8 -x 8 -s 8 -k 2M",
             "-o", f"{last_part}.%(ext)s",
             "--restrict-filenames",
             master])
    elif sys_argv == "subs":
        print("SUB")
        subprocess.run(
            ["yt-dlp",
             "--write-subs",
             "--skip-download",
             "-o", f"{last_part}.%(ext)s",
             "--restrict-filenames",
             master])
    elif sys_argv == "both":
        print("BOTH")
        subprocess.run(
            ["yt-dlp",
             "-f", "bv*+mergeall[vcodec=none]",
             "--audio-multistreams",
             "--write-subs",
             "--embed-subs",
             "--external-downloader", "aria2c",
             "--external-downloader-args", "-c -j 8 -x 8 -s 8 -k 2M",
             "-o", f"{last_part}.%(ext)s",
             "--restrict-filenames",
             master])
