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
    posts = reddit.subreddit(parse_sub).hot(limit=5)

    #clears files
    files = glob.glob('content/*')
    for f in files:
        os.remove(f)
    files = glob.glob('videos/*')
    for f in files:
        os.remove(f)

    for post in posts:

        #reset variables
        text = []
        words = []
        text_segments = [""]
        text_drawings = []
        length = 0
        delay = 0

        if post.stickied == False:

            #set up title
            post.title = post.title.replace("/", " or ")
            title_audio = gTTS(text = post.title, lang = "en", slow = False).save("content/title_audio.mp3")
            title_text = TextClip(txt=post.title, font='Tahoma-Bold', align="west", fontsize=28, size=(650, 300),
                                  color="white", method="caption").set_position(("center", 600)).set_duration(
                AudioFileClip("content/title_audio.mp3").duration)
            background_image = ImageClip("./background.png").set_start(0).set_duration(
                AudioFileClip("content/title_audio.mp3").duration).set_pos(("center", 500)).resize(1.1, 1.1)
            delay = AudioFileClip("content/title_audio.mp3").duration + 1
            #add to video


            #set up text
            post.selftext = post.selftext.replace("\n", "")
            text_audio = gTTS(text = post.selftext, lang = "en", slow = False).save("content/text_audio.mp3")
            #splits text into an array of segments for video
            words = post.selftext.split(" ")
            i = 0
            for word in words:
                length += len(word)
                text_segments[len(text_segments) - 1] += (word + " ")
                if length > 40 or "." in word or "," in word:
                    length = 0
                    text_segments.append("")

            for i in range(0, len(text_segments) - 1):
                text_audio = gTTS(text= text_segments[i] + " a", lang="en", slow=False).save("content/audio_segment" + str(i) + ".mp3")

            #combine background video, and set audio
            randomint = random.randrange(1700)
            video = VideoFileClip("./backgroundmovie.mp4").resize((1080, 1920)).subclip(randomint, randomint + 300)
            final_audio = CompositeAudioClip([AudioFileClip("content/title_audio.mp3"), AudioFileClip("content/text_audio.mp3").
                                             set_start(AudioFileClip("content/title_audio.mp3").duration + 1)]).set_fps(44100)
            final_audio.write_audiofile("content/final_audio.mp3")
            video = video.set_audio(AudioFileClip("content/final_audio.mp3"))
            text_drawings.append(video)
            text_drawings.append(background_image)
            text_drawings.append(title_text)

            #create text drawings from text
            for i in range(0, len(text_segments) - 1):

                text_drawing = (TextClip(txt=text_segments[i],
                                              font='Tahoma-Bold',
                                              align="center", fontsize=50, size=(900,300), color="white",
                                              method="caption")
                                               .set_position(("center", "center")))
                text_drawing.save_frame("content/text_drawing" + str(i) + ".png")
                text_drawings.append(text_drawing.set_start(delay)
                                     .set_duration(AudioFileClip("content/audio_segment" + str(i) + ".mp3").duration - 0.50))
                delay += AudioFileClip("content/audio_segment" + str(i) + ".mp3").duration - 0.50

            final_video = CompositeVideoClip(text_drawings).set_duration(AudioFileClip("content/final_audio.mp3").duration)
            final_video.write_videofile("videos/" + post.title + "#reddit" + ".mp4", fps=30)

