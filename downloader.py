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
            "outtmpl": f"./downloads/{filename}.%(ext)s",
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
            "outtmpl": f"./downloads/{filename}.%(ext)s",
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
            "outtmpl": f"./downloads/{filename}.%(ext)s",
            "windowsfilenames":True,
            "verbose":True,
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
    page_id = jupiter_url.split("/")[-2]
    for item in driver.requests:
        if f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}" in item.url:
            jupiter_url = item.url
            print(f"DATA-URL = {jupiter_url}")
    
    #Get season and episode data from JSON
    content = requests.get(jupiter_url).json()
    seasons = content["data"]["seasonList"]["items"]
    print("\nAvailable seasons and episodes:")
    index = 0
    for s in seasons:
        if "name" in s.keys():
            print("Season",s["name"])
        else:
            print("Season 1")
        if "active" in s.keys():
            string = ""
            for e in s["contents"]:
                string+=f"{e["episode"]},"
            print("\tEpisodes:",string[0:-1])
        #Get non-active season json
        else:
            page_id = s["firstContentId"]
            jupiter_url = f"https://jupiter.err.ee/{page_id}"
            driver.get(jupiter_url)
            for item in driver.requests:
                if f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}" in item.url:
                    jupiter_url = item.url
                    print(f"DATA-URL = {jupiter_url}")
            seasons[index]["contents"] = requests.get(jupiter_url).json()["data"]["seasonList"]["items"][index]["contents"]
            for e in seasons[index]["contents"]:
                string+=f"{e["episode"]},"
            print("\tEpisodes:",string[0:-1])
        index+=1
    
    episodes = seasons[0]["contents"]
    
    #Download every episode from season
    for item in episodes:
        print(f"URL={item["url"]}")
        url = item["url"]
        filename = url.split("/")[-1]+f"-S{item["season"]}E{item["episode"]}"
#        download_video(url, filename, sys_argv)
