# AutoJumpCut_and_exomake
ジャンプカットの自動化 and その動画をAviutilに自動配置  

# サンプルコマンド　
## Jumpcut.py   
動画の無音区間削除プログラム  
-mm ゲームなどメインの動画  
-ms メインの動画の音声  
-v 自分の音声などの無音カットしたい音声(ここにメインの動画の音声を入れてもいいよ・・・多分)  

```
 python .\Jumpcut.py -mm ..\video001.mp4 -ms ..\audio002.m4a -v audio003.m4a 1 1
```

## make_exo.py
無音区間を削除した細かい動画をタイムいライン上に自動配置したAviutl のプロジェクトファイルを作成するプログラム  
-mrf メインのジャンプカット結果が入ったフォルダ  
-msrf メイン動画の音声のジャンプカット動画が入ったフォルダ  
-vrf 自分の音声などのジャンプカット結果が入ったフォルダ  
-tm 以下に説明記載  
tm = "1" 動画と同じ時間に配置する(数フレームの誤差あり)  
tm, = "0" 左詰めで配置する  
```
python .\make_exe.py -mrf ..\Jumpcut_result -msrf ..\Jumpcut_result_sound\ -vrf ..\jumpcut_result_vocie_0\ --tm "0"
```

