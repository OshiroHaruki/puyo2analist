import cv2
import numpy as np
import puyo_simulator
import os

def resize_img(img):
    WIDE = 640
    HEIGHT = 360
    return cv2.resize(img,(WIDE, HEIGHT))

def cut_img_1p(img):
    return img[:,0:320]

def bgr2hsv(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def calc_videotime(video_fps, num_frame):
    """
    Args:
        video_fps: 動画のFPS
        num_frame: 何フレーム目か
    """
    # 何秒か計算して出力
    second = num_frame/video_fps
    minute = second//60
    return "{:0>2d}:{:0>2d}".format(int(minute), int(second%60))

def pickup_color(img,low_hsv_value, high_hsv_value):
    """HSV画像から指定の色を読み取り白黒画像で返す.
    Args:
        img : HSV色空間の画像
        low_hsv_value (list[3]): [H,S,V]
        high_hsv_value (list[3]): [H,S,V]
    Returns:
        mask_img: マスク画像
    """
    hsv_low = np.array(low_hsv_value)
    hsv_high = np.array(high_hsv_value)
    mask_img = cv2.inRange(img, hsv_low, hsv_high)
    return mask_img

def make_mask_imgs(img):
    """6色(ぷよの種類)分のマスク画像を生成する。
    Args:
        img : BGR色空間の画像

    Returns:
        mask_imgs(list): 6枚のマスク画像(黄色、赤、青、紫、緑、おじゃま(灰))
    """
    img = bgr2hsv(img)
    
    hsv_range = [   [[6,121,178],[32,255,255]], 
                    [[[0, 64, 100], [4, 220, 255]], [[165, 64, 100], [179, 220, 255]] ],
                    [[96, 105, 158], [123, 255, 255]], 
                    [[135, 45, 161], [144, 255, 255]],
                    [[41, 108, 115], [57, 241, 255]],
                    [[0,0,85], [180,20,255]]
                ]
    mask_imgs = []
    for color_hsv_list in hsv_range:
        mask_img = np.zeros((360, 320))
        if isinstance(color_hsv_list[0][0], list) == True:
            for c in color_hsv_list:
                m = pickup_color(img, c[0], c[1])
                mask_img += m
        else:
            m = pickup_color(img, color_hsv_list[0], color_hsv_list[1])
            mask_img += m
        mask_imgs.append(mask_img)
    return mask_imgs

def puyo_search(mask_img, x_pos, y_pos):
    """指定座標にぷよがあるか判定する.
    Args:
        mask_img: マスク画像
        x_pos: マスのx座標
        y_pos: マスのy座標
    Return:
        (bool): ぷよがあるかないか
    """
    X_FIELD_POS = 90
    X_SQUARE = 21
    X_RANGE_START = 6
    X_RANGE = 10
    Y_FIELD_POS = 55
    Y_SQUARE = 20
    Y_RANGE_START = 5
    Y_RANGE = 10
    x_pos_on_img = x_pos * X_SQUARE + X_RANGE_START + X_FIELD_POS
    y_pos_on_img = y_pos * Y_SQUARE + Y_RANGE_START + Y_FIELD_POS
    
    x = x_pos_on_img
    y = y_pos_on_img
    
    for _ in range(Y_RANGE):
        for _ in range(X_RANGE):
            if mask_img[y][x] == 255:
                return True
            else:
                x += 1
        x = x_pos_on_img
        y += 1
    return False

def make_field(mask_imgs):
    """盤面を配列での情報へ変換する.
    Args:
        mask_imgs: mask画像が格納されたリスト
    """
    # YELLOW = 1, RED = 2, BLUE = 3 PURPLE = 4, GREEN = 5, OJAMA = 6
    COLOR = [1, 2, 3, 4, 5, 6]
    field = [[0]*6 for _ in range(12)]
    
    for y in range(11, -1, -1):
        for x in range(6):
            for c in range(len(COLOR)):
                if puyo_search(mask_imgs[c], x, y):
                    field[y][x] = COLOR[c]
                    if y != 11 and field[y+1][x] == 0:# 下が何もないなら、上にも何もない.
                        field[y][x] = 0
                    break
    return field

def check_tsumo(prev_img, img):
    """動体検知を行い、ツモ判定を行う.
    """
    # ツモ枠の位置
    TSUMO_FRAME = [[240,50],[255,85],[265,132]]
    # 動体検知する範囲の大きさ
    D = 5

    tsumo_move = 0
    for i in range(3):
        x = TSUMO_FRAME[i][0]
        y = TSUMO_FRAME[i][1]
        prev_frame = prev_img[y:y+D, x:x+D]
        gray_prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray_prev_frame = gray_prev_frame.astype("float")
        
        frame = img[y:y+D, x:x+D]
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        cv2.accumulateWeighted(gray_frame, gray_prev_frame, 0.9)
        frame_delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(gray_prev_frame))
        thresh = cv2.threshold(frame_delta, 3, 255, cv2.THRESH_BINARY)[1]
        amount_of_change = np.sum(thresh)
        k = D**2 * (2/3) # 2/3程度動体検知できていれば動いていると判定する。
        if amount_of_change > k:
            tsumo_move += 1
    return tsumo_move == 3

def check_multiple_mark(source_img, target_img):
    gray_img = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
    match_result = cv2.matchTemplate(gray_img, target_img, cv2.TM_CCOEFF_NORMED)
    
    threshold = 0.7
    loc = np.where(match_result >= threshold)
    if not loc:
        return False
    if loc[0].size == 0:
        return False
    if (loc[0][0] > 290) and (loc[0][0] < 317):
        if (loc[1][0] > 85) and (loc[1][0] < 230):
            return True
    return False

def check_score_0000(source_img, target_img):
    gray_img = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
    result_match_0000 = cv2.matchTemplate(gray_img, target_img,cv2.TM_CCOEFF_NORMED)
    threshold = 0.95 #敷居値(0~1)
    #検出結果から検出領域の位置を取得
    loc=np.where(result_match_0000 >= threshold)
    return loc[0].size != 0

def movie_process(target_file, output_folder="result"):
    output_file_path = f"./{output_folder}/result.csv"
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
        resized_img = resize_img(img)       
        img_1p = cut_img_1p(resized_img)
        if prev_img is None:
            prev_img = img_1p
            continue

        if match_started_flag and check_score_0000(resized_img, score_0000_img):
            # 試合の区切りを判定.
            match_count += 1
            match_started_flag = False
        
        # 連鎖後にツモ欄が動いているか判定
        tsumo_flag = check_tsumo(prev_img, img_1p)
        if(tsumo_flag and (next_flag == False)):
            match_started_flag = True
            next_flag = True
            num_puyo_after = puyo_function.count_puyo()
            output_file.write(f"{num_puyo_after}\n")
            next_flag = True

        # ✖️が出てきたら
        kakeru_flag = check_multiple_mark(img_1p, kakeru_img)
        if(kakeru_flag and next_flag):
            mask_imgs = make_mask_imgs(img_1p) #マスク画像を生成
            # 連鎖数を読み取る
            puyo_function.field = make_field(mask_imgs) # 盤面を配列の情報にする.
            num_puyo_before = puyo_function.count_puyo() # ぷよ量カウント
            num_chain = puyo_function.chain() # 連鎖数
            movie_time = calc_videotime(video_fps, frame_count) # 動画時間
            output_file.write(f"{movie_time}, {match_count}, {num_chain}, {num_puyo_before}, ") # 結果の書き込み
            next_flag = False
            # 次に前のフレームまでツモ欄が動く(next_flag=true)まではスルー.
        prev_img = img_1p # 更新

    output_file.close()