import os
import cv2
import puyo_simulator
import numpy as np
import movie_process as m

def reverse_img(img):
    # 画像を反転させる
    return cv2.flip(img, 1)

def movie_process_2p(target_file, output_folder="result"):
    output_file_path = f"./{output_folder}/result_2p.csv"
    if os.path.isdir(output_folder) == False:
        os.mkdir(output_folder)
    
    cap_file = cv2.VideoCapture(target_file)
    output_file = open(output_file_path, "w")
    output_file.write("動画時間, 試合, 連鎖数, 発火前ぷよ量, 発火後ぷよ量\n")

    print(f"動画読み込み成否->{cap_file.isOpened()}")

    kakeru_img = cv2.imread("./kakeru.png", 0)
    kakeru_img = cv2.resize(kakeru_img,(12,12))
    score_0000_img = cv2.imread("./score_0000.png", 0)

    # 各変数の初期化
    next_flag = True
    prev_img = None
    match_started_flag = True
    frame_count = 0
    match_count = 0
    num_puyo_before = 0
    num_puyo_after = 0

    # ゲームシミュレータを格納.
    puyo_function = puyo_simulator.puyo_simulator()

    # 動画のfpsを取得
    video_fps = cap_file.get(cv2.CAP_PROP_FPS)

    #画像を1フレームずつ取得。終わったらループを抜ける
    while True:
        frame_count += 1
        ret, img = cap_file.read()
        if not ret:
            break
        resized_img = m.resize_img(img)
        reversed_img = reverse_img(resized_img)
        img_2p = m.cut_img_1p(reversed_img)
        if prev_img is None:
            prev_img = img_2p
            continue

        if match_started_flag and m.check_score_0000(resized_img, score_0000_img):
            # 試合の区切りを判定.
            match_count += 1
            match_started_flag = False
        
        # 連鎖後にツモ欄が動いているか判定
        tsumo_flag = m.check_tsumo(prev_img, img_2p)
        if(tsumo_flag and (next_flag == False)):
            match_started_flag = True
            next_flag = True
            num_puyo_after = puyo_function.count_puyo()
            output_file.write(f"{num_puyo_after}\n")
            next_flag = True

        # ✖️が出てきたら
        kakeru_flag = m.check_multiple_mark(img_2p, kakeru_img)
        if(kakeru_flag and next_flag):
            mask_imgs = m.make_mask_imgs(img_2p) #マスク画像を生成
            # 連鎖数を読み取る
            puyo_function.field = m.make_field(mask_imgs) # 盤面を配列の情報にする.
            num_puyo_before = puyo_function.count_puyo() # ぷよ量カウント
            num_chain = puyo_function.chain() # 連鎖数
            movie_time = m.calc_videotime(video_fps, frame_count) # 動画時間
            output_file.write(f"{movie_time}, {match_count}, {num_chain}, {num_puyo_before}, ") # 結果の書き込み
            next_flag = False
            # 次に前のフレームまでツモ欄が動く(next_flag=true)まではスルー.
            cv2.imwrite(f"a{frame_count}.png", img_2p)
        prev_img = img_2p # 更新

    output_file.close()