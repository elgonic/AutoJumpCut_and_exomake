import glob  # リスト取得
import pathlib  # globと似てるこっちのほうが便利らしい
import subprocess
from re import sub
import os  # パス接続
import sys
import argparse  # コマンドライン実装

RESULT_VOICE_FNAME = "jumpcut_result_vocie"
RESULT_MOVIE_FNAME = "Jumpcut_result"
RESULT_SOUND_FNAME = "Jumpcut_result_sound"


def main():
    # コマンドライン
    input_command = argparse.ArgumentParser(
        description="JupCut プログラム")  # インスタンス生成
    input_command.add_argument(
        "-mm", "--main_movie", help="Main movie ex. Gamingplay movie")
    input_command.add_argument(
        "-ms", "--main_sound", help="Main sound ex. Gamingplay movie sound")
    input_command.add_argument(
        "-v", "--voice", nargs="*", action="append",  help="Extract zone ex. Playing voice")
    input_inf = input_command.parse_args()  # 引数をパース

    # main 処理
    #input_movie_path = "D:\program\movie_easy\JumpCut_note_DT\IMG_1966.MOV"
    input_movie_path = os.path.abspath(input_inf.main_movie)
    main_movie_path = os.path.abspath(input_inf.main_movie)
    print(main_movie_path)
    main_sound_path = os.path.abspath(input_inf.main_sound)
    print("main sound path =" + main_sound_path)

    if input_inf.voice is not None:
        # 入力ボイス格納
        voice = []  # (1: ファイルへのpath , 2: フロント余白時間, 3: バック余白時間)
        for voice_file in input_inf.voice:  # (余白時間が無い場合0を挿入する)
            print(voice_file)
            print(len(voice_file))
            while(len(voice_file) <= 2):
                voice_file.append("0")
            voice.append(voice_file)
        print(voice)
        print(input_inf.voice)
    else:
        flont_space: float = 0
        back_space: float = 0

    calent_dir = os.path.dirname(input_movie_path)
    print(calent_dir)
    os.chdir(calent_dir)

    #  結果入力フォルダー作成(main movie 用)
    try:
        print(os.mkdir(RESULT_MOVIE_FNAME))
    except FileExistsError:
        print("File is Exists")
    #  結果入力フォルダー作成(main voice 用)
    try:
        print(os.mkdir(RESULT_SOUND_FNAME))
    except FileExistsError:
        print("File is Exists")
    # 結果入力フォルダー作成(voice 用)
    if input_inf.voice is not None:
        for i in range(len(input_inf.voice)):
            try:
                os.mkdir(RESULT_VOICE_FNAME+"_"+"{number}".format(number=i))
            except FileExistsError:
                print("File is Exists")

    if input_inf.voice is not None:
        for count, i in enumerate(voice):
            print(voice)
            print("aaaa="+i[1])
            input_movie_path = os.path.abspath(i[0])
            print(input_movie_path)
            flont_space = float(i[1])
            back_space  = float(i[2])
            silence_zone = extract_silentzone(
                input_movie_path, flont_space, back_space)
            mk_jupcut(RESULT_VOICE_FNAME+"_"+str(count), silence_zone, input_movie_path)
        mk_jupcut(RESULT_MOVIE_FNAME, silence_zone, main_movie_path) # 本当なら複数のvoice の無音区間を結合する
        mk_jupcut(RESULT_SOUND_FNAME, silence_zone, main_sound_path)

    else:
        silence_zone = extract_silentzone(
                input_movie_path, flont_space, back_space)
        mk_jupcut(RESULT_MOVIE_FNAME, silence_zone, input_movie_path)

# 無音区間の抽出
# flontspace , back_space = 前後の余分時間


def extract_silentzone(input_movie_path, flont_space, back_space):
    silent_zone = subprocess.run(["ffmpeg", "-i", input_movie_path, "-af", "silencedetect=noise=-30dB:d=0.4",
                                 "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(silent_zone.stdout.decode("utf8")) なぜかエラーになっておるのでstdrerrに格納される
    # print(silent_zone.stderr.decode("utf8"))
    # silent_zone = silent_zone.stdout.decode("utf8")
    silent_zone = str(silent_zone)
    silent_zone = silent_zone.split("\\r\\n")
    # silent start , end の抽出
    delete_time_list = []
    for line in silent_zone:
        if "silencedetect" in line:
            words = line.split(" ")
            for i in range(len(words)):
                if "silence_start" in words[i]:
                    silence_start = float(words[i+1])+flont_space
                    if float(words[i+1]) == 0:
                        delete_time_list.append(float(words[i+1]))
                    else:
                        delete_time_list.append(silence_start)
                if "silence_end" in words[i]:
                    silence_end = float(words[i+1])-back_space
                    if float(words[i+1]) - back_space <= 0:
                        delete_time_list.append(0)
                    elif silence_start >= silence_end : # 猶予時間によって無音区間がマイナスになった場合その区間削除
                        del delete_time_list[-1]
                    
                    #猶予時間によって前の動画と同じ区間を抽出してしまうことを防ぐ
                    else:
                        delete_time_list.append(silence_end)


               

    starts_ends_times = list(zip(*[iter(delete_time_list)]*2))
    print("start_ends_times=" + str(starts_ends_times))
    return starts_ends_times


def mk_jupcut(result_folder,starts_ends_times, movie_name):
    print(range(len(starts_ends_times)-1))
    result_folder = os.path.abspath(result_folder)
    filename_extention = os.path.splitext(movie_name)
    for i in range(len(starts_ends_times)-1):
        start_time = starts_ends_times[i][1] # 有音区間の始まり = 無音区間の終わり
        end_time = starts_ends_times[i+1][0] # 有音区間の終わり = 無音区間の始まり
        splitfile = os.path.join(result_folder, str(i)+"_"+str(start_time)+"_"+str(end_time) + filename_extention[1])
        print(splitfile)
        output = subprocess.run(["ffmpeg", "-i", movie_name, "-ss", str(start_time), "-t", str(end_time-start_time) , splitfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_movie_inf(movie_path):
    movie_inf = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,duration",
                               "-of", "default=nokey=1:noprint_wrappers=1", movie_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    movie_inf = movie_inf.stdout.decode("utf8")
    movie_inf = movie_inf.splitlines()
    print(float(movie_inf[1]) * float(eval(movie_inf[0])))
    return movie_inf


if __name__ == "__main__":
    main()
