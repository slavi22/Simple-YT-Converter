from flask import Flask, request, render_template, send_file, after_this_request
from pytube import YouTube
from configparser import ConfigParser
import io
import os
import ffmpeg

config = ConfigParser()
config.read("config.ini")
app = Flask(__name__, template_folder = config['Template.folder']['path'])
link = None
video_name = None
video = None
audio = None


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/converted", methods=['POST'])
def converted_page():
    global link
    link = request.form.get("videoLink")
    yt = YouTube(link)
    global video_name
    video_name = yt.title
    return render_template("converted.html", title = yt.title, link = link) #https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/6
#https://stackoverflow.com/questions/68149318/download-a-file-without-storing-it

#thats what im trying to do now -- https://stackoverflow.com/questions/71820529/how-do-i-combine-pytube-audio-and-video-streams-in-a-flask-app-and-let-the-user
@app.route("/converted/download", methods=['GET'])
def download_video():
    pull_videos()
    return convert_video()


# https://www.google.com/search?q=how+to+merge+faster+with+ffmpeg+python&ei=mdcUZIfNLeGOxc8PxaWBkAs&oq=how+to+merge+faster+with+ffmpeg+pyt&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAxgAMgcIIRCgARAKOgoIABBHENYEELADOgUIIRCgAToICCEQFhAeEB06CgghEBYQHhAPEB1KBAhBGABQsARY6A5gixtoAXABeACAAc4BiAGiBZIBBTAuMy4xmAEAoAEByAEIwAEB&sclient=gws-wiz-serp -- do this because right now it encodes it thats why it takes so slow
def pull_videos(): 
    global link, video_name
    yt = YouTube(link)
    video = yt.streams.filter(res="1080p").first() #use itag to get resolution and fps
    video.download(filename=f"{video_name}.mp4")
    audio= yt.streams.filter(only_audio=True).first()
    audio.download(filename=f"{video_name}.mp3")

#https://stackoverflow.com/questions/24612366/delete-an-uploaded-file-after-downloading-it-from-flask -- used 'Garrett's solution on how to load the out.mp4 to memory (buffer)
#https://stackoverflow.com/questions/74233100/merging-audio-and-video-in-ffmpeg-python-is-too-slow -- used the method posted by 'Rotem' on copying over instead of reencoding the audio and video together
def convert_video():
    input_video = ffmpeg.input(f"{video_name}.mp4")
    input_audio = ffmpeg.input(f"{video_name}.mp3")
    #ffmpeg.concat(input_video, input_audio, v=1, a=1).output("out.mp4").run() -- this is very slow but also works
    ffmpeg.output(input_audio, input_video, "out.mp4", codec="copy").run()
    file_path = "out.mp4"
    return_data = io.BytesIO()
    with open(file_path, "rb") as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(f"{video_name}.mp4")
    os.remove(f"{video_name}.mp3")
    os.remove(file_path)
    return send_file(return_data, as_attachment=True, download_name=f"{video_name}.mp4", mimetype=f"{video_name}/mp4")

#https://github.com/JNYH/pytube/blob/master/pytube_sample_code.ipynb -- find a way to do this somehow??, kind of did idk??
if __name__ == '__main__':
    app.run(debug=True, port=5600)