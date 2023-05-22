from moviepy.editor import *
from gtts import *
import secret as s
import random
import os
import glob
import praw

if __name__ == '__main__':

    parse_sub = "amitheasshole"
    text = []
    words = []
    text_segments = [""]
    text_drawings = []
    length = 0
    delay = 0

    reddit = praw.Reddit(client_id=s.CLIENT_ID,
                         client_secret=s.CLIENT_SECRET,
                         username=s.USERNAME, password=s.PASSWORD,
                         user_agent="ammarkhawaja")
    posts = reddit.subreddit(parse_sub).hot(limit=3)

    #CLEARS FILES
    files = glob.glob('content/*')
    for f in files:
        os.remove(f)

    for post in posts:
        if post.stickied == False:
            post.title = post.title.replace("/", " or ")
            post.selftext = post.selftext.replace("\n", "")
            text_audio = gTTS(text = post.selftext, lang = "en", slow = False).save("content/text_audio.mp3")
            #splits text into an array of segments for video
            words = post.selftext.split(" ")
            i = 0
            for word in words:
                length += len(word)
                text_segments[len(text_segments) - 1] += (word + " ")
                if length > 5 or "." in word:
                    length = 0
                    text_segments.append("")
                i+=1
                if i > 10:
                    break
            for i in range(0, len(text_segments) - 1):
                text_audio = gTTS(text=word[i], lang="en", slow=False).save("content/audio_segment" + str(i) + ".mp3")

            #get background video and audio
            randomint = random.randrange(2000)
            video = VideoFileClip("./backgroundmovie.mp4").resize((1080, 1920)).subclip(randomint, randomint + 60)
            video = video.set_audio(AudioFileClip("content/text_audio.mp3"))
            text_drawings.append(video)

            #create text drawings from text
            for i in range(0, len(text_segments) - 1):

                text_drawing = (TextClip(txt=text_segments[i],
                                              font='Tahoma-Bold',
                                              align="center", fontsize=100, size=(650,300), color="white",
                                              method="caption")
                                               .set_position(("center", "center")))
                text_drawing.save_frame("content/text_drawing" + str(i) + ".png")
                text_drawings.append(text_drawing.set_start(delay)
                                     .set_duration(AudioFileClip("content/audio_segment" + str(i) + ".mp3").duration))
                delay += AudioFileClip("content/audio_segment" + str(i) + ".mp3").duration

            final_video = CompositeVideoClip(text_drawings).set_duration(5)
            final_video.write_videofile("content/" + post.title + ".mp4", fps=30)

