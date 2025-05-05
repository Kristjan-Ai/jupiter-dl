from conf import conf, paths
debugging = conf["debugging"]
import requests
import yt_dlp
import traceback
import re

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
        if debugging: print(f"\t{corrections}")
        index = 0
        for f in info["formats"]:
            fkeys = f.keys()
            #Set video language to None
            if f["audio_ext"]=="none":
                info['formats'][index]['language']="und"
                if debugging: print(f"\t {f["format"]} language set to und")
            #Replace language tag according to corrections dict
            elif "language" in fkeys:
                flang = f["language"]
                if flang in corrections.keys():
                    if debugging: print(f"\t{flang} -> {corrections[flang]}")
                    info['formats'][index]['language']=corrections[flang][0]
                    info['formats'][index]["title"]=corrections[flang][1] #Doesn't work
            index+=1
        return [], info

def download_video(url, filename, mode, dl_path, overwrite):
    filename = re.sub(r'\/','-',  filename) #filenames shouldn't create folders / -> -
    dl_path += "/" if dl_path[-1] != "/" else ""
    if mode == "video":
        if debugging: print("Only video")
        ydl_opts = {
            "format":"bv*[acodec=none]+mergeall[vcodec=none][protocol=http_dash_segments]",
            "allow_multiple_audio_streams":True,
            "external_downloader":"aria2c",
            "external_downloader_args":"-c -j 8 -x 8 -s 8 -k 2M",
            "postprocessors":[{"key":"FFmpegMetadata"}],
            "outtmpl": f"{dl_path}{filename}.%(ext)s",
            "windowsfilenames":True,
            "overwrites":overwrite,
            "test":False,
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
    elif mode == "subs":
        if debugging: print("SUB")
        ydl_opts = {
            "writesubtitles":True,
            "skip_download":True,
            "outtmpl": f"{dl_path}{filename}.%(ext)s",
            "windowsfilenames":True,
            "overwrites":overwrite,
            "test":False,
            }
#         subprocess.run(
#             ["C:/bin/yt-dlp.exe",
#              "--write-subs",
#              "--skip-download",
#              "-o", f"{filename}.%(ext)s",
#              "--restrict-filenames",
#              url])
    elif mode == "both":
        if debugging: print("BOTH")
        ydl_opts = {
            "format":"bv*[acodec=none]+mergeall[vcodec=none][protocol=http_dash_segments]",
            "allsubtitles":True,
            "writesubtitles":True,
            "allow_multiple_audio_streams":True,
            "external_downloader":"aria2c",
            "external_downloader_args":"-c -j 8 -x 8 -s 8 -k 2M",
            "postprocessors":[{"key":"FFmpegMetadata"},{"key":"FFmpegEmbedSubtitle"}],
            "outtmpl": f"{dl_path}{filename}.%(ext)s",
            "windowsfilenames":True,
            "overwrites":overwrite,
            "test":False,
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
        
def get_jupiter_video(jupiter_url, mode, path, create_folder, debug, overwrite):
    if debug:
        global debugging
        debugging = True
    #Get JSON for metadata
    page_id = jupiter_url.split("/")[3]
    json_data = requests.get(f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}").json()
    maincontent = json_data["data"]["mainContent"]
    title = maincontent["originalTitle"] if maincontent["originalTitle"]!="" else maincontent["heading"]
    filename = f"{title} ({maincontent["year"]})"
    path += filename+"/" if create_folder else ""
    try:
        download_video(jupiter_url, filename, mode, path, overwrite)
    except Exception:
        if debugging: print(traceback.format_exc())
   
def get_jupiter_series(jupiter_url, mode, path, create_folder, debug, overwrite):
    if debug:
        global debugging
        debugging = True
    #Get JSON for episode links
    page_id = jupiter_url.split("/")[3]
    json_data = requests.get(f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}").json()
    series_title = json_data["data"]["mainContent"]["originalTitle"] if json_data["data"]["mainContent"]["originalTitle"]!="" else json_data["data"]["mainContent"]["heading"]
    series_year = json_data["data"]["mainContent"]["year"]

    #Get season and episode data from JSON
    try:
        content = json_data["data"]["seasonList"]["items"]
    except:
        print("ERROR: Could not find episodes. Is this a series?")
        quit()
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
        
        else:
            #Get non-active season json
            page_id = s["firstContentId"]
            data_url = f"https://services.err.ee/api/v2/vodContent/getContentPageData?contentId={page_id}"
            #print(f"DATA-URL = {data_url}")
            json = requests.get(data_url).json()
            #Add season json to dictionary
            seasons[s["name"]] = json["data"]["seasonList"]["items"][index]["contents"]
            string = ""
            for e in seasons[s["name"]]:
                string+=f"{e["episode"]},"
            print("\tEpisodes:",string[0:-1])
        index+=1

    #Get user choice
    choice = {}
    episodes = []
    print("Choose episodes by season to download (example: 1-2,5,7-8 or all or leave empty)")
    for s in seasons.keys():
        choice[s] = input(f"Season {s} episodes:").split(",")
        
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
                index = 0
                for e in seasons[s]:
                    if str(e["episode"]) == str(c):
                        episodes.append(seasons[s][index])
                    index+=1
            elif c == "all" or c == "kõik":
                #yt-dlp won't download duplicates
                episodes += seasons[s][:]
                break
            elif c != "":
                print(f"ERROR Wrong format: {c}")
    
    #Download every episode from season
    path += f"{series_title} ({series_year})/" if create_folder else ""
    if page_id in paths.keys(): path = paths[page_id]
    for item in episodes:
        url = item["url"]
        if debugging: print(f"URL = {url}")
        season_episode = f"S{("0" if item["season"]<10 else "")}{item["season"]}E{("0" if item["episode"]<10 else "")}{item["episode"]}"
        title = item["subHeading"] if item["subHeading"]!="" else series_title
        filename = f"{season_episode} - {title}"
        episode_path = path+f"Season {item["season"]}/" if create_folder else path
        print(filename)
        try:
            download_video(url, filename, mode, episode_path, overwrite)
        except Exception:
            if debugging: print(traceback.format_exc())
