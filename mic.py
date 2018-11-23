# -*- coding:utf-8 -*-

import pyaudio
import numpy as np
import threading
import subprocess
import pygame.mixer
import time

CHUNK = 1024*2 # マイクによって変わる。上手くいかない場合色々試してください
RATE = 48000 # 事前に確認したサンプリング周波数
JUDGE_INTERVAL = 5 # 騒音検知インターバル

max_data = []
angry_count = 0

p = pyaudio.PyAudio()

stream = p.open(format = pyaudio.paInt16,
        channels = 1,
        rate = RATE,
        frames_per_buffer = CHUNK,
        input = True,
        output = True)

def audio_trans(input):
    frames = (np.frombuffer(input,dtype = "int16"))
    max_data.append(max(frames))
    return

def angry(level):
    # mixerモジュールの初期化
    pygame.mixer.init(frequency = 48000, size = -16, channels = 2, buffer = 1024)
    # 音楽ファイルの読み込み
    if level == 1:
        pygame.mixer.music.load("level1.mp3")
    elif level == 2:
        pygame.mixer.music.load("level2.mp3")
    elif level == 3:
        pygame.mixer.music.load("level3.mp3")
    else:
        pygame.mixer.music.load("shitsukoi.mp3")
    
    # 音楽再生、および再生回数の設定(-1はループ再生)
    pygame.mixer.music.play(1)
    time.sleep(10)
    # 再生の終了
    pygame.mixer.music.stop()

# 現在の音量を取得し、うるさければ注意
def judge(): # 定期的に呼び出される
    global max_data
    global angry_count
    if len(max_data) != 0: # 初回実行時だけ無視
        mic_ave = int(sum(max_data)/len(max_data)) # 60秒間のマイク受信音量の平均値を出す
        max_data = []
        volume_text = '音量:{0}' . format(mic_ave)
        print(max_data)
        try:
            print (volume_text)
            if angry_count > 5:
                print ('しつこーい')
                angry_count = 0
                angry(4)
            elif mic_ave > 900:
                print ('angry level three')
                angry_count += 1
                angry(3)
            elif mic_ave > 700:
                print ('angry level two')
                angry_count += 1
                angry(2)
            elif mic_ave > 400:
                print ('angry level one')
                angry_count += 1
                angry(1)

        except:
            print ("error")

    t = threading.Timer(JUDGE_INTERVAL, judge) #60秒ごとにjudgeを実行
    t.start()

t = threading.Thread(target = judge)
t.start()

print ("mic on")

while stream.is_active():
    input = stream.read(CHUNK)
    input = audio_trans(input)

stream.stop_stream()
stream.close()
p.terminate()

print ("Stop Streaming")
