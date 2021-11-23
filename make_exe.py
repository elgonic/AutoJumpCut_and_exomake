import pathlib  # globと似てるこっちのほうが便利らしい
import subprocess
from re import sub
import os  # パス接続
import argparse  # コマンドライン実装
import decimal


RESULT_PATH = os.getcwd()


def main():
    # Valiavles
    now_flame = 1  # 現在のフレーム
    layer = 1  # 初期レイヤー

    # コマンドライン
    input_command = argparse.ArgumentParser(
        description="exo make プログラム")  # インスタンス生成
    input_command.add_argument(
        "-mrf", "--main_result_folder", help="Main movie result folder ex. Gamingplay movie jumpcut result into folder")
    input_command.add_argument(
        "-msrf", "--main_sound_result_folder", help="Main sound result folder. Gamingplay movie sound jumpcut into folder")
    input_command.add_argument(
        "-vrf", "--voice_result_folder", nargs="*",  help="voice_result_folder ex. Playing voice jumpcut result into folder")

    input_command.add_argument(
        "-tm", "--time_mode", default="0", help="voice_result_folder ex. Playing voice jumpcut result into folder")
    input_inf = input_command.parse_args()  # 引数をパース
    # main 処理
    main_movie_path = os.path.abspath(input_inf.main_result_folder)
    print("main movie path =" + main_movie_path)
    main_sound_path = os.path.abspath(input_inf.main_sound_result_folder)
    print("main sound path =" + main_sound_path)

    if input_inf.voice_result_folder is not None:
        # 入力ボイス格納
        voice_path = []  # (1: ファイルへのpath , 2: フロント余白時間, 3: バック余白時間)
        for voice_file in input_inf.voice_result_folder:  # (余白時間が無い場合0を挿入する)
            voice_path.append(os.path.abspath(voice_file))
    file_list = get_result_file_list(voice_path[0])

    # exo file 作成
    exo_file = open(os.path.join(RESULT_PATH, "output.exo"), mode="w")

# ***********作成途中*******************

    # カットした動画の処理

    # 動画処理
    layer = layer
    movie_result_file_list = get_result_file_list(main_movie_path)

    # 動画のフレームレートを取得する
    fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of",
                         "default=nokey=1:noprint_wrappers=1", movie_result_file_list[0]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fps = int(eval(fps.stdout.decode("utf8")))

    # ファイルの初めの部分(プロジェクトのフレームレートなど)
    # ここは新規プロジェクトを作成しないときにexoを取り込んだ時にこの情報でプロジェクトが作成される
    # 今は適当に決め打ちしとく いずれ GUI で決定
    print("[exedit]", file=exo_file)
    print("width=", 1920, sep="", file=exo_file)
    print("hight=", 1080, sep="", file=exo_file)
    print("rate=", fps, sep="", file=exo_file)  # 文字列計算関数　eval
    print("scale=", 1, sep="", file=exo_file)
    print("langh=", 1, sep="", file=exo_file)
    print("audio_rate=", 44100, sep="", file=exo_file)
    print("audio_ch=", 2, sep="", file=exo_file)

    # 動画配置モード取得
    Placement_mode = input_inf.time_mode
    print("Placement_mode = " + Placement_mode)

    if Placement_mode == "0":  # 左詰め配置
        for count, file in enumerate(movie_result_file_list):
            # Python は 参照渡し　気をつけろ
            movie_exo_make(file, now_flame, exo_file, count, layer)
            # 次回のスタートフレーム数=今回の終わりのフレーム数+1
            now_flame = now_flame + get_flame(file)+1
            print(now_flame)

        # 動画音声処理
        layer = layer + 1
        movie_sound_result_file_list = get_result_file_list(main_sound_path)
        # count は　前のfor から引き継がれてる 初期化されていない
        # mainmovie 用 カウント変数
        n = 0
        now_flame = 1
        for count, file in enumerate(movie_sound_result_file_list, count + 1):
            movie_sound_exo_make(
                file, movie_result_file_list[n], now_flame, exo_file, count, layer)
            now_flame = now_flame + get_flame(movie_result_file_list[n])+1
            n = n+1
        # 音声処理 今回は１個だけ ゆくゆくは複数指定可能にする
        # 音声処理 上記に配置した動画の時間に対応した箇所に配置する
        layer = layer + 1
        voice_list = get_result_file_list(voice_path[0])
        n = 0
        now_flame = 1
        for count, file in enumerate(voice_list, count + 1):
            voice_exo_make(
                file, movie_result_file_list[n], now_flame, exo_file, count, layer, fps)
            now_flame = now_flame + get_flame(movie_result_file_list[n])+1
            n = n + 1

    elif Placement_mode == "1":  # 動画時間配置
        for count, file in enumerate(movie_result_file_list):
            now_flame = convert_time_to_flame(get_file_start_time(file), fps)
            # Python は 参照渡し　気をつけろ
            movie_exo_make(file, now_flame, exo_file, count, layer)
            print(now_flame)

        # 動画音声処理
        layer = layer + 1
        movie_sound_result_file_list = get_result_file_list(main_sound_path)
        # count は　前のfor から引き継がれてる 初期化されていない
        # mainmovie 用 カウント変数
        n = 0
        for count, file in enumerate(movie_sound_result_file_list, count + 1):
            now_flame = convert_time_to_flame(get_file_start_time(file), fps)
            movie_sound_exo_make(
                file, movie_result_file_list[n], now_flame, exo_file, count, layer)
            n = n+1
        # 音声処理 今回は１個だけ ゆくゆくは複数指定可能にする
        # 音声処理 上記に配置した動画の時間に対応した箇所に配置する
        layer = layer + 1
        voice_list = get_result_file_list(voice_path[0])
        n = 0
        for count, file in enumerate(voice_list, count + 1):
            now_flame = convert_time_to_flame(get_file_start_time(file), fps)
            voice_exo_make(
                file, movie_result_file_list[n], now_flame, exo_file, count, layer, fps)
            n = n + 1


#    for file in file_list:
#        root, ext = os.path.splitext(file)
#        if ext == ".mp4":  # 個々の条件式はAvitul の設定から持ってくる
#            movie_exo_make(file, now_flame, exo_file)
#        else:
#            voice_exo_make(file, now_flame, exo_file)
#

#  結果ファイルリスト取得
def get_result_file_list(folder_path):
    remove_file(folder_path, "lwi") #一度exoファイルを作成したときに出るゴミの削除
    file_list = list(pathlib.Path(folder_path).glob("*"))
    if(len(file_list) == 0):
        print("フォルダ内にファイルがありません")
        print(quit)
    get_file_number(file_list[2])
    # file_list をソート = ループする
    file_list = sorted(file_list, key=get_file_number)
    return file_list


def remove_file(folder_path, extension):
    for file in list(pathlib.Path(folder_path).glob("*." + extension)):
        os.remove(file)

def get_file_number(file_path):
    # ファイル名　 取得 <- 元か らfolder path を取得すればいらないのでは
    file_name=os.path.basename(file_path)
    file_number=int(file_name.split("_")[0])  # 結果ファイル名は 番号_開始時間_終了時間なので
    return file_number


def get_file_start_time(file_path):
    file_start_time=os.path.basename(file_path)
    file_start_time=float(file_start_time.split("_")[1])
    print(file_start_time)
    return file_start_time


def get_file_end_time(file_path):
    file_end_time=os.path.basename(file_path)
    file_end_time=float(file_end_time.split("_")[2])
    return file_end_time


def get_flame(file_path):
    flame=subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames",
                            "-of", "default=nokey=1:noprint_wrappers=1", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    flame=flame.stdout.decode("utf8").rstrip("\r\n")
    return int(flame)


def convert_time_to_flame(time, fps): #やっぱり数フレームずれる(1フレームぐらい)
    time = float(decimal.Decimal(str(time)).quantize(decimal.Decimal("0.001"), rounding=decimal.ROUND_HALF_UP ) )
    flame=time * fps 
    flame = float(decimal.Decimal(str(flame)).quantize(decimal.Decimal("0"), rounding=decimal.ROUND_UP ) )
    flame = flame + 3 
    print("a=",flame , time)
    return flame


def movie_exo_make(file_path, now_flame, exo_file, count, layer):
    n=count
    flame=get_flame(file_path)
    e_flame=now_flame + flame

    # []　動画順番
    print('[', n, ']', sep="", file=exo_file)  # sep 区切り文字　デフォ半角スペース
    print('start=', now_flame, sep="", file=exo_file)
    print('end=', e_flame, sep="", file=exo_file)
    print('layer=', layer, sep="", file=exo_file)  # 映像ファイル1,音声ファイル2
    print('group=', n+1, sep="", file=exo_file)
    print('overlay=', 1, sep="", file=exo_file)
    print('camera=', 0, sep="", file=exo_file)
    print('[''{:.1f}'']'.format(n), sep="", file=exo_file)
    print('_name=動画ファイル', sep="", file=exo_file)  # 音声ファイルでは音声ファイルにする
    print('再生位置=', 1, sep="", file=exo_file)
    print('再生速度=', 100.0, sep="", file=exo_file)
    print('ループ再生=', 0, sep="", file=exo_file)
    print('アルファチャンネルを読み込む=', 0, sep="", file=exo_file)
    print('file=', file_path,  sep="", file=exo_file)
    print('[', n+0.1, ']', sep="", file=exo_file)
    print('_name=標準描画', sep="", file=exo_file)
    print('X=', 0.0, sep="", file=exo_file)  # 座標 X,Y,Z
    print('Y=', 0.0, sep="", file=exo_file)
    print('Z=', 0.0, sep="", file=exo_file)
    print('拡大率=', 100.00, sep="", file=exo_file)
    print('透明度=', 0.0, sep="", file=exo_file)
    print('回転=''{:.2f}'.format(0.00), sep="", file=exo_file)
    print('blend=', 0, sep="", file=exo_file)


def movie_sound_exo_make(file_path, movie_path, now_flame, exo_file, count, layer):
    n=count
    flame=get_flame(movie_path)
    e_flame=now_flame + flame

    # []　動画順番
    print('[', n, ']', sep="", file=exo_file)  # sep 区切り文字　デフォ半角スペース
    # 動画start-end ffmpegは動画でやったのでいらない
    print('start=', now_flame, sep="", file=exo_file)
    print('end=', e_flame, sep="", file=exo_file)
    print('layer=',  layer, sep="", file=exo_file)  # 音声ファイル2
    print('group=', n+1, sep="", file=exo_file)  # nのまま
    print('overlay=', 1, sep="", file=exo_file)
    print('audio=', 1, sep="", file=exo_file)  # ここ　動画にはなかった　代わりにcamera　削除
    print('[''{:.1f}'']'.format(n), sep="", file=exo_file)
    print('_name=音声ファイル', sep="", file=exo_file)  # 音声ファイルでは音声ファイルにする
    print('再生位置=''{:.2f}'.format(0.00), sep="", file=exo_file)  # 動画では1だった
    print('再生速度=', 100.0, sep="", file=exo_file)
    print('ループ再生=', 0, sep="", file=exo_file)
    print('動画ファイルと連携=', 0, sep="", file=exo_file)  # 今回動画と音背別だから連携できないかも
    print('file=', file_path, sep="", file=exo_file)
    print('[', n+0.1, ']', sep="", file=exo_file)
    print('_name=標準再生', sep="", file=exo_file)  # 動画では標準描画　音声　標準再生
    print('音量=', 100.0, sep="", file=exo_file)
    print('左右=', 0.0, sep="", file=exo_file)


def voice_exo_make(file_path, movie_path, now_flame, exo_file, count, layer, fps):
    n=count
    flame=get_flame(movie_path)
    e_flame=now_flame + flame

#    s_time = get_file_start_time(file_path)
#    flame = convert_time_to_flame(s_time , fps)
#    e_flame = now_flame + flame

    # []　動画順番
    print('[', n, ']', sep="", file=exo_file)  # sep 区切り文字　デフォ半角スペース
    # 動画start-end ffmpegは動画でやったのでいらない
    print('start=', now_flame, sep="", file=exo_file)
    print('end=', e_flame, sep="", file=exo_file)
    print('layer=', layer, sep="", file=exo_file)  # 音声ファイル2
    print('group=', n+1, sep="", file=exo_file)  # nのまま
    print('overlay=', 1, sep="", file=exo_file)
    print('audio=', 1, sep="", file=exo_file)  # ここ　動画にはなかった　代わりにcamera　削除
    print('[''{:.1f}'']'.format(n), sep="", file=exo_file)
    print('_name=音声ファイル', sep="", file=exo_file)  # 音声ファイルでは音声ファイルにする
    print('再生位置=''{:.2f}'.format(0.00), sep="", file=exo_file)  # 動画では1だった
    print('再生速度=', 100.0, sep="", file=exo_file)
    print('ループ再生=', 0, sep="", file=exo_file)
    print('動画ファイルと連携=', 0, sep="", file=exo_file)
    print('file=', file_path, sep="", file=exo_file)
    print('[', n+0.1, ']', sep="", file=exo_file)
    print('_name=標準再生', sep="", file=exo_file)  # 動画では標準描画　音声　標準再生
    print('音量=', 100.0, sep="", file=exo_file)
    print('左右=', 0.0, sep="", file=exo_file)


if __name__ == "__main__":
    main()
