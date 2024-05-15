import yt_dlp
from json.encoder import JSONEncoder

URL = "https://lasteekraan.err.ee/1609206455/kadunud-sokid"

# ℹ️ See help(yt_dlp.postprocessor.PostProcessor)
class MyCustomPP(yt_dlp.postprocessor.PostProcessor):
    def run(self, info):
        self.to_screen('Correcting metadata')
        corrections = {
            "ch":["und","Originaal"],
            "nl":["et","Vaegnägijad"],
            }
        index = 0
        for f in info["formats"]:
            fkeys = f.keys()
            #Set video language to None
            if f["audio_ext"]=="none":
                info['formats'][index]['language']="und"
                print(f"\t {f["format_id"]} language set to und")
            #Replace language tag according to corrections dict
            if "language" in fkeys:
                flang = f["language"]
                if flang in corrections.keys():
                    print(f"\t{flang} -> {corrections[flang]}")
                    info['formats'][index]['language']=corrections[flang][0]
                    info['formats'][index]["title"]=corrections[flang][1]
            index+=1
        return [], info

with yt_dlp.YoutubeDL() as ydl:
    ydl.add_post_processor(MyCustomPP(), when='pre_process')
    info = ydl.extract_info(URL, download=False)
    f = open("./jupiter.json", "w")
    f.write(JSONEncoder().encode(info))
    f.close()
    