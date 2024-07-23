from conf import *
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
import subprocess
import requests
import yt_dlp

class MyCustomPP(yt_dlp.postprocessor.PostProcessor):
    def run(self, info):
        self.to_screen('Correcting metadata')
#        if "und" in info["subtitles"]:
#            info["subtitles"]["et"]=info["subtitles"]["und"]
        corrections = {
            "ch":["und","Originaal"],
            "nl":["et","Vaegnägijad"],
            "und":["und","Originaal"],
            }
        index = 0
        for f in info["formats"]:
            fkeys = f.keys()
            #Set video language to None
            if f["audio_ext"]=="none":
                info['formats'][index]['language']="und"
                print(f"\t {f["format"]} language set to und")
            #Replace language tag according to corrections dict
            elif "language" in fkeys:
                flang = f["language"]
                if flang in corrections.keys():
                    print(f"\t{flang} -> {corrections[flang]}")
                    info['formats'][index]['language']=corrections[flang][0]
                    info['formats'][index]["title"]=corrections[flang][1]
            index+=1
        return [], info

def download_video(url, filename, sys_argv):
    if sys_argv == "dl":
        print("DL")
        ydl_opts = {
            "format":"bv*+mergeall[vcodec=none][protocol=m3u8_native]",
            "allow_multiple_audio_streams":True,
            "external_downloader":"aria2c",
            "external_downloader_args":"-c -j 8 -x 8 -s 8 -k 2M",
            "postprocessors":[{"key":"FFmpegMetadata"}],
            "outtmpl": f"{dl_dir}{filename}.%(ext)s",
            "windowsfilenames":True,
            }
#         subprocess.run(
#             ["C:/bin/yt-dlp.exe",
#              "-f", "bv*+mergeall[vcodec=none][protocol=m3u8_native]",
#              "--audio-multistreams",
#              "--embed-metadata",
#              "--embed-subs",
#              "--external-downloader", "aria2c",
#              "--external-downloader-args", "-c -j 8 -x 8 -s 8 -k 2M",
#              "-o", f"{filename}.%(ext)s",
#              "--restrict-filenames",
#              url])
    elif sys_argv == "subs":
        print("SUB")
        ydl_opts = {
            "writesubtitles":True,
            "skip_download":True,
            "outtmpl": f"{dl_dir}{filename}.%(ext)s",
            "windowsfilenames":True,
            }
#         subprocess.run(
#             ["C:/bin/yt-dlp.exe",
#              "--write-subs",
#              "--skip-download",
#              "-o", f"{filename}.%(ext)s",
#              "--restrict-filenames",
#              url])
    elif sys_argv == "both":
        print("BOTH")
        ydl_opts = {
            "format":"bv*+mergeall[vcodec=none][protocol=m3u8_native]",
            "allsubtitles":True,
            "writesubtitles":True,
            "allow_multiple_audio_streams":True,
            "external_downloader":"aria2c",
            "external_downloader_args":"-c -j 8 -x 8 -s 8 -k 2M",
            "postprocessors":[{"key":"FFmpegMetadata"},{"key":"FFmpegEmbedSubtitle"}],
            "outtmpl": f"{dl_dir}{filename}.%(ext)s",
            "windowsfilenames":True,
            }
#         subprocess.run(
#             ["C:/bin/yt-dlp.exe",
#              "-f", "bv*+mergeall[vcodec=none][protocol=m3u8_native]",
#              "--audio-multistreams",
#              "--embed-metadata",
#              "--write-subs",
#              "--embed-subs",
#              "--external-downloader", "aria2c",
#              "--external-downloader-args", "-c -j 8 -x 8 -s 8 -k 2M",
#              "-o", f"{filename}.%(ext)s",
#              "--restrict-filenames",
#              "--verbose",
#              url])
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(MyCustomPP(), when='pre_process')
        ydl.download([url])
        
def get_jupiter_video(jupiter_url, sys_argv):
    parts = jupiter_url.split("/")
    last_part = parts[-1]
    download_video(jupiter_url, last_part, sys_argv)

        
        
def get_jupiter_series(jupiter_url, sys_argv):
    # Create a new instance of the Firefox driver in headless mode
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(
        options=options
    )

    # Go to the Jupiter link
    driver.get(jupiter_url)
    print(f"URL = {jupiter_url}")
    
    #Get JSON for episode links
    page_id = jupiter_url.split("/")[3]
    for item in driver.requests:
        if f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}" in item.url:
            print(f"DATA-URL = {item.url}")
            json_data = requests.get(item.url).json()
            break
    
    #Get season and episode data from JSON
    content = json_data["data"]["seasonList"]["items"]
    seasons = {}
    print("\nAvailable seasons and episodes:")
    index = 0
    for s in content:
        if "name" in s.keys():
            print("Season",s["name"])
            season = s["name"]
        else:
            print("Season 1")
            season = "1"
        if "active" in s.keys():
            seasons[season] = s["contents"]
            string = ""
            for e in s["contents"]:
                string+=f"{e["episode"]},"
            print("\tEpisodes:",string[0:-1])
        #Get non-active season json and add to current json
        else:
            page_id = s["firstContentId"]
            jupiter_url = f"https://jupiter.err.ee/{page_id}"
            driver.get(jupiter_url)
            success = False
            for item in driver.requests:
                if f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}" in item.url:
                    print(f"DATA-URL = {item.url}")
                    success = True
                    json = requests.get(item.url).json()
                    seasons[s["name"]] = json["data"]["seasonList"]["items"][index]["contents"]
                    string = ""
                    for e in seasons[s["name"]]:
                        string+=f"{e["episode"]},"
                    print("\tEpisodes:",string[0:-1])
                    break
            if not success:
                print(f"Couldn't find season {s["name"]} json url")
        index+=1
    driver.quit()
    #Get user choice
    choice = {}
    episodes = []
    for s in seasons.keys():
        choice[s] = input("Choose season "+s+" episodes (example: 1-2,5,7-8):").split(",")
        
    for s in choice.keys():
        for c in choice[s]:
            if "-" in c:
                r = list(map(int,c.split("-")))
                index = 0
                for e in seasons[s]:
                    if e["episode"] in range(r[0],r[1]+1):
                        episodes.append(seasons[s][index])
                    index+=1
            elif c.isdecimal():
                episodes.append(seasons[s][int(c)])
    
    #Download every episode from season
    for item in episodes:
        print(f"URL={item["url"]}")
        url = item["url"]
        filename = f"S{item["season"]}E{item["episode"]} - "+url.split("/")[-1]
        print(filename)
        try:
            download_video(url, filename, sys_argv)
        except Exception as e:
            print(f"ERROR downloading {filename}")
