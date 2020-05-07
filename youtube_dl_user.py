from __future__ import unicode_literals
import msvcrt
from urllib.request import urlopen
from bs4 import BeautifulSoup
import youtube_dl
import os
import sys
import json
import re


def my_hook(d):
    if d["status"] == "finished":
        file_tuple = os.path.split(os.path.abspath(d["filename"]))
        print("Done downloading {}".format(file_tuple[1]))
    if d["status"] == "downloading":
        print(d["filename"], d["_percent_str"], d["_eta_str"])


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


audio_location = ""
video_location = ""

with open("youtube_options.json") as file:
    data = json.load(file)
    audio_location = data["audio_location"]
    video_location = data["video_location"]


class Video:
    title = ""
    url = ""
    i = 0

    def __init__(self, title, url, i):
        self.title = title
        self.url = url
        self.i = i


def get_videos(search_term):
    i = 1
    videos = []
    search_inp = search_term.replace(" ", "+")
    page = urlopen(f"http://www.youtube.com/results?search_query={search_inp}")
    soup = BeautifulSoup(page, "html.parser")
    for link in soup.findAll("a", {"title": not None}):
        href = link.get("href")
        if "/watch" in href and "list" not in href:
            title = link.get("title")
            url = f"http://www.youtube.com{href}"
            video = Video(title, url, i)
            videos.append(video)
            i += 1
        if i == 10:
            return videos


def get_video_location():
    place = msvcrt.getch()
    if place == b"`":
        return ""
    c = int(place)
    if c == 0:
        exit(1)

    print("Loading...")
    return c - 1


def download(url, option):
    with youtube_dl.YoutubeDL(ydl_opts[option]) as ydl:
        try:
            ydl.download([url])
        except:
            pass


def show(videos):
    for video in videos:
        print(f"{video.i}. {video.title}")


def get_selected_format(inp):
    return inp.split(" -f ")[1] if len(inp.split(" -f ")) > 1 else "a"


while True:
    user_input = input("Search or place in link: ")
    option = get_selected_format(user_input)
    if "www.you" in user_input:
        splitted = user_input.split(" ")
        if len(splitted) > 1 and splitted[1] != "mp3":
            audio_location += "/" + splitted[1] + "/"
            video_location += "/" + splitted[1] + "/"
        video_url = user_input
        if "playlist" in user_input or (len(splitted) > 1 and splitted[1] == "mp3"):
            ydl_opts = {
                "a": {
                    "format": "bestaudio",
                    "outtmpl": fr"{audio_location}\%(title)s.%(ext)s",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                    "logger": MyLogger(),
                    "progress_hooks": [my_hook],
                }
            }
        else:
            ydl_opts = {
                "a": {
                    "format": "bestaudio",
                    "outtmpl": fr"{audio_location}\%(title)s.%(ext)s",
                    "logger": MyLogger(),
                    "progress_hooks": [my_hook],
                }
            }
        download(video_url, option)
    else:
        videos = get_videos(user_input)
        show(videos)
        choice = get_video_location()
        video_url = videos[choice].url
        ydl_opts = {
            "v": {
                "format": "137",
                "outtmpl": fr"{video_location}\%(title)s.%(ext)s",
                "logger": MyLogger(),
                "progress_hooks": [my_hook],
            },
            "a": {
                "format": "bestaudio",
                "outtmpl": fr"{audio_location}\%(title)s.%(ext)s",
                "logger": MyLogger(),
                "progress_hooks": [my_hook],
            },
        }
        try:
            download(video_url, option)
        except:
            pass
