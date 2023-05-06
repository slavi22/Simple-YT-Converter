from flask import Flask, request, render_template, send_file, session, make_response
from pytube import YouTube
from pytube.cli import on_progress
from configparser import ConfigParser
import io
import os
import ffmpeg
import re
import secrets
import random
import shutil

config = ConfigParser()
config.read("config.ini")
app = Flask(__name__, template_folder = config['Template.folder']['path'])
secret = secrets.token_urlsafe()
app.secret_key = secret
sessionId = None
link = None
video_name = None
video = None
audio = None
resolution = None

@app.route("/")
def index():
    session["session"] = ""
    resp = make_response(render_template("index.html"))
    global sessionId
    sessionId = request.cookies.get("session")
    return resp

# https://github.com/pytube/pytube/issues/1453#issuecomment-1382458877 -- fixed the slow loading of the page - pytube issue not flask -- old doesnt work anymore
# https://github.com/pytube/pytube/issues/1553#issuecomment-1532902806 -- fixed the newly introduced slow download issue - 06.05.2023 -- new
@app.route("/converted", methods=['POST'])
def converted_page():
    global link
    link = request.form.get("videoLink")
    yt = YouTube(link)
    global video_name
    pattern = "\s*[\\/:*?\"<>|]"
    video_name = re.sub(pattern, "", yt.title)
    global resolution
    resolution = get_itags_for_video(yt)
    #print(f"resolution is: {resolution}")
    if("r1080_60" in resolution):
        if(resolution["r1080_60"] != None or resolution["r720_60"] != None or resolution["r480"] != None or resolution["r360"] != None):
            return render_template(
                "converted.html", title = yt.title, fps = "60fps", video_thumbnail = yt.thumbnail_url,
                render_1080_table = True if(resolution['r1080_60']!=None) else False, r1080 = "1080p - 60fps" if (resolution['r1080_60']!=None) else "", r1080_file_size= f"{round(yt.streams.get_by_itag(resolution['r1080_60']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r1080_60']!=None) else "",
                render_720_table = True if(resolution['r720_60']!=None) else False, r720 = "720p - 60fps" if (resolution['r720_60']!=None) else "", r720_file_size= f"{round(yt.streams.get_by_itag(resolution['r720_60']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r720_60']!=None) else "",
                render_480_table = True if(resolution['r480']!=None) else False, r480 = "480p" if (resolution['r480']!=None) else "", r480_file_size= f"{round(yt.streams.get_by_itag(resolution['r480']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r480']!=None) else "",
                render_360_table = True if(resolution['r360']!=None) else False, r360 = "360p" if (resolution['r360']!=None) else "", r360_file_size = f"{round(yt.streams.get_by_itag(resolution['r360']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r360']!=None) else "",
                mp3_file_type = "MP3", mp3_file_size = f"{round(yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB")
    else:
        if(resolution['r1080_30']!=None or resolution['r720_30'] != None or resolution['r480'] != None or resolution['r360'] != None):
            return render_template(
                "converted.html", title = yt.title, fps = "30fps", video_thumbnail = yt.thumbnail_url,
                render_1080_table = True if(resolution['r1080_30']!=None) else False, r1080 = "1080p - 30fps" if (resolution['r1080_30']!=None) else "", r1080_file_size= f"{round(yt.streams.get_by_itag(resolution['r1080_30']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r1080_30']!=None) else "",
                render_720_table = True if(resolution['r720_30']!=None) else False, r720 = "720p - 30fps" if (resolution['r720_30']!=None) else "", r720_file_size= f"{round(yt.streams.get_by_itag(resolution['r720_30']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r720_30']!=None) else "",
                render_480_table = True if(resolution['r480']!=None) else False, r480 = "480p" if (resolution['r480']!=None) else "", r480_file_size= f"{round(yt.streams.get_by_itag(resolution['r480']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r480']!=None) else "",
                render_360_table = True if(resolution['r360']!=None) else False, r360 = "360p" if (resolution['r360']!=None) else "", r360_file_size = f"{round(yt.streams.get_by_itag(resolution['r360']).filesize_mb + yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB" if (resolution['r360']!=None) else "",
                mp3_file_type = "MP3", mp3_file_size = f"{round(yt.streams.filter(only_audio=True).first().filesize_mb, 1)} MB")


#https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/6
#https://stackoverflow.com/questions/68149318/download-a-file-without-storing-it


def get_itags_for_video(yt: YouTube):
    dict60 = {"r1080_60": None, "r720_60": None, "r480": None, "r360": None}
    dict30 = {"r1080_30": None, "r720_30": None, "r480": None, "r360": None}
    for x in yt.streams:
        try:
            if(f"{x.resolution} {x.fps}"=="1080p 60"):
                dict60["r1080_60"] = x.itag
            if(f"{x.resolution} {x.fps}"=="1080p 30" or f"{x.resolution} {x.fps}" == "1080p 25" or f"{x.resolution} {x.fps}" == "1080p 24"):
                dict30["r1080_30"] = x.itag
            if(f"{x.resolution} {x.fps}"=="720p 60"):
                dict60["r720_60"] = x.itag
            if(f"{x.resolution} {x.fps}"=="720p 30" or f"{x.resolution} {x.fps}" == "720p 25" or f"{x.resolution} {x.fps}" == "720p 24"):
                dict30["r720_30"] = x.itag
            if(f"{x.resolution}"=="480p"):
                dict30["r480"] = x.itag
                dict60["r480"] = x.itag
            if(f"{x.resolution}"=="360p"):
                dict30["r360"] = x.itag
                dict60["r360"] = x.itag
        except AttributeError:
            ""
    if(dict60["r1080_60"]!=None or dict60["r720_60"]!=None):
        return dict60
    else:
        return dict30


#thats what im trying to do now -- https://stackoverflow.com/questions/71820529/how-do-i-combine-pytube-audio-and-video-streams-in-a-flask-app-and-let-the-user
@app.route("/converted/download/1080p60fps", methods=['GET'])
def download_converted_video_1080p60fps():
    download_video_1080p_60fps()
    return convert_video()

@app.route("/converted/download/720p60fps", methods=['GET'])
def download_converted_video_720p60fps():
    download_video_720p_60fps()
    return convert_video()

@app.route("/converted/download/1080p30fps", methods=['GET'])
def download_converted_video_1080p30fps():
    download_video_1080p_30fps()
    return convert_video()

@app.route("/converted/download/720p30fps", methods=['GET'])
def download_converted_video_720p30fps():
    download_video_720p_30fps()
    return convert_video()

@app.route("/converted/download/480p", methods=['GET'])
def download_converted_video_480p30fps():
    download_video_480p()
    return convert_video()

@app.route("/converted/download/360p", methods=['GET'])
def download_converted_video_360p30fps():
    download_video_360p()
    return convert_video()

@app.route("/converted/download/mp3", methods=['GET'])
def download_mp3():
    download_mp3_locally()
    return convert_audio()
# https://www.google.com/search?q=how+to+merge+faster+with+ffmpeg+python&ei=mdcUZIfNLeGOxc8PxaWBkAs&oq=how+to+merge+faster+with+ffmpeg+pyt&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAxgAMgcIIRCgARAKOgoIABBHENYEELADOgUIIRCgAToICCEQFhAeEB06CgghEBYQHhAPEB1KBAhBGABQsARY6A5gixtoAXABeACAAc4BiAGiBZIBBTAuMy4xmAEAoAEByAEIwAEB&sclient=gws-wiz-serp -- do this because right now it encodes it thats why it takes so slow

def create_session_folder():
    global sessionId
    path = f'./{sessionId}'
    if not os.path.exists(path):
        os.makedirs(path)


def download_mp3_locally():
    global link, video_name, sessionId
    create_session_folder()
    yt = YouTube(link)
    yt.streams.filter(only_audio=True).first().download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")

#figure out the itags cuz they dont match between videos
def download_video_1080p_60fps(): 
    global link, video_name, resolution, sessionId
    create_session_folder()
    yt = YouTube(link)
    video = yt.streams.get_by_itag(resolution["r1080_60"]) #use itag to get resolution and fps
    video.download(filename=f"{video_name}.mp4", output_path=f"./{sessionId}")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")

def download_video_720p_60fps(): 
    global link, video_name, resolution, sessionId
    create_session_folder()
    yt = YouTube(link)
    video = yt.streams.get_by_itag(resolution["r720_60"])
    video.download(filename=f"{video_name}.mp4", output_path=f"./{sessionId}")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")   

def download_video_1080p_30fps(): 
    global link, video_name, resolution, sessionId
    create_session_folder()
    yt = YouTube(link)
    video = yt.streams.get_by_itag(resolution["r1080_30"])
    video.download(filename=f"{video_name}.mp4", output_path=f"./{sessionId}")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")

def download_video_720p_30fps(): 
    global link, video_name, resolution, sessionId
    create_session_folder()
    yt = YouTube(link)
    video = yt.streams.get_by_itag(resolution["r720_30"])
    video.download(filename=f"{video_name}.mp4", output_path=f"./{sessionId}")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")

def download_video_480p(): 
    global link, video_name, resolution, sessionId
    create_session_folder()
    yt = YouTube(link)
    video = yt.streams.get_by_itag(resolution["r480"])
    video.download(filename=f"{video_name}.mp4", output_path=f"./{sessionId}")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")

def download_video_360p(): 
    global link, video_name, resolution, sessionId
    create_session_folder()
    yt = YouTube(link)
    video = yt.streams.get_by_itag(resolution["r360"])
    video.download(filename=f"{video_name}.mp4", output_path=f"./{sessionId}")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3", output_path=f"./{sessionId}")



#https://stackoverflow.com/questions/24612366/delete-an-uploaded-file-after-downloading-it-from-flask -- used 'Garrett's solution on how to load the out.mp4 to memory (buffer)
#https://stackoverflow.com/questions/74233100/merging-audio-and-video-in-ffmpeg-python-is-too-slow -- used the method posted by 'Rotem' on copying over instead of reencoding the audio and video together
def convert_video():
    global video_name, sessionId   
    input_video = ffmpeg.input(f"./{sessionId}/{video_name}.mp4")
    input_audio = ffmpeg.input(f"./{sessionId}/{video_name}.mp3")
    #ffmpeg.concat(input_video, input_audio, v=1, a=1).output("out.mp4").run() -- this is very slow but also works
    ffmpeg.output(input_audio, input_video, f"./{sessionId}/out.mp4", codec="copy").run()
    converted_file = f"./{sessionId}/out.mp4"
    return_data = io.BytesIO()
    with open(converted_file, "rb") as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    # os.remove(f"{video_name}.mp4")
    # os.remove(f"{video_name}.mp3")
    # os.remove(converted_file)
    shutil.rmtree(f"./{sessionId}", ignore_errors=True)
    return send_file(return_data, as_attachment=True, download_name=f"{video_name}.mp4", mimetype="video/mp4") #mimetype should not include any lets say bulgarians characters as it breaks the encoding, thats why i put the mimetype to be 'video/mp4' instead of '{video_name}/mp4'

def convert_audio():
    global video_name, sessionId
    input_audio = ffmpeg.input(f"./{sessionId}/{video_name}.mp3")
    #cant use .mp3 extension for the out file below because it throws an exception because apparently u cant use codec='copy' if u have 2 mp3s
    ffmpeg.output(input_audio, f"./{sessionId}/out.mp4", codec="copy").run() 
    downloaded_file = f"./{sessionId}/out.mp4"
    return_data = io.BytesIO()
    with open(downloaded_file, "rb") as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    # os.remove(f"{video_name}.mp3")
    # os.remove(downloaded_file)
    shutil.rmtree(f"./{sessionId}", ignore_errors=True)
    return send_file(return_data, as_attachment=True, download_name=f"{video_name}.mp3", mimetype="audio/mp4")

#https://github.com/JNYH/pytube/blob/master/pytube_sample_code.ipynb -- find a way to do this somehow??, kind of did idk??
if __name__ == '__main__':
    app.run(debug=True, port=5600)
