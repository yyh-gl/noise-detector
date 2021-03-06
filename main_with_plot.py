import queue
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import pygame.mixer
import time
from datetime import datetime


def audio_callback(indata, outdata, frames, time, status):
    """サンプリングごとに呼ばれるコールバック関数"""
    #if status:
    #    print(status, file=sys.stderr)

    # ここのコメントを外すと取得した音声をそのまま出力する
    #outdata[:] = indata

    global q
    q.put(indata)


def update_plot(frame):
    """matplotlibのアニメーション更新毎に呼ばれるグラフ更新関数"""

    global plotdata
    global total_volumes
    global volumes
    global count

    count += 1
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break

        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

        # 取得音量を保存
        volumes = list(map(lambda num: abs(num) , data))
        total_volumes += sum(volumes)

        # 5秒ごとに騒音判定
        if count == 5:
            count = 0
            # 音量の平均値を用いて騒音検知
            average_volume = total_volumes / (len(volumes) * 5)
            judge(average_volume)
            total_volumes = 0

        lines[0].set_ydata(plotdata[:, 0])

    return lines

def judge(average_volume):
    """怒り判定する関数"""

    global angry_count

    print("\n")
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    print(average_volume)
    try:
        if angry_count >= 4:
            print ('しつこーい')
            angry_count = 0
            angry(0)
        elif average_volume > 0.2:
            print ('怒りレベル：3')
            angry(3)
            angry_count += 1
        elif average_volume > 0.1:
            print ('怒りレベル：2')
            angry(2)
            angry_count += 1
        elif average_volume > 0.06:
            print ('怒りレベル：1')
            angry(1)
            angry_count += 1

    except Exception as e:
        print ("error")
        print(e.args)

def angry(level):
    """怒る関数"""

    global q

    # mixerモジュールの初期化
    pygame.mixer.init(frequency = 48000, size = -16, channels = 2, buffer = 1024)

    # 音楽ファイルの読み込み
    if level == 1:
        pygame.mixer.music.load("level1.wav")
        sleep_time = 6
    elif level == 2:
        pygame.mixer.music.load("level2.wav")
        sleep_time = 5
    elif level == 3:
        pygame.mixer.music.load("level3.wav")
        sleep_time = 5
    else:
        pygame.mixer.music.load("shitsukoi.wav")
        sleep_time = 8

    # 音楽再生、および再生回数の設定(-1はループ再生)
    pygame.mixer.music.play(1)
    time.sleep(sleep_time)

    # スリープ中もデータ取得するしているのでクリアする
    q = queue.Queue()

    # 再生の終了
    pygame.mixer.music.stop()


if __name__ == '__main__':
    samplerate = 48000   # サンプリング周波数
    window = 0.2         # グラフ表示サンプル数決定係数
    interval = 1000      # グラフ更新頻度（ミリ秒）
    channels = 1         # チャンネル数（1固定）

    q = queue.Queue()

    total_volumes = 0
    angry_count = 0
    count = 0

    length = int(window * samplerate)   # グラフに表示するサンプル数
    plotdata = np.zeros((length, 1))
    volumes = []

    fig, ax = plt.subplots()
    lines = ax.plot(plotdata)          # グラフのリアルタイム更新の最初はプロットから
    ax.axis((0, len(plotdata), -1, 1))

    stream = sd.Stream(channels=channels, samplerate=samplerate, callback=audio_callback)
    ani = FuncAnimation(fig, update_plot, interval=interval, blit=False)
    with stream:
        plt.show()
