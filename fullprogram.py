from moviepy.editor import *
from tkinter.filedialog import *

import requests
from keysecret import api_key_assemblyai
import sys

#CONVERT THE VIDEO TO AN AUDIO CLIP-- ask with tkinter and convert with moviepy.editor
video = askopenfilename()
clip = VideoFileClip(video)
audio = clip.audio

audio.write_audiofile("extracted_audio.mp3")

#Use assembly AI to analyze audio file and create a json
# upload
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

headers = {'authorization': api_key_assemblyai}

filename = "extracted_audio.mp3"  #sys.argv[1] originally

def upload(filename):
    def read_file(filename, chunk_size=5242880):  #number is how many bits of audio information is sent to ai
        with open(filename,'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    
    upload_response = requests.post(upload_endpoint,
                         headers=headers,
                         data=read_file(filename))


    audio_url = upload_response.json()["upload_url"]
    return audio_url

#transcribe
def transcribe(audio_url):
    transcript_request = { "audio_url": audio_url }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    
    job_id = transcript_response.json()['id']
    return job_id

#poll
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)   #send data = post only getting use get
    return polling_response.json()

def get_transcription_results_url(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data["error"]

audio_url = upload(filename)
data, error = get_transcription_results_url(audio_url)

#convert text json from assembly AI to captions using moviepy, new fonts were added in type-ghostwrite.xml file of magick program files

clip = VideoFileClip("IMG_6100.mp4")
txt_clips = [clip]

user = input("Which Font? (albas, orange_juice, and proximanova are 3rd party fonts installed): ")

for word_number in range(len(data["words"])):
    txt = data["words"][word_number]["text"]
    start = data["words"][word_number]["start"]/1000
    end = data["words"][word_number]["end"]/1000

    txt_clip = TextClip(txt, fontsize = 140, color = 'black', font = user)  
    txt_clip = txt_clip.set_pos('center').set_start(start).set_end(end).set_duration(end - start)
    txt_clips += [txt_clip]

video = CompositeVideoClip(txt_clips)  
video.ipython_display(width = 280)  
