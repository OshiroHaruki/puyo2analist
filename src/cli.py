import sys
import movie_process
import os

# 動画ファイルを実行時に引数で指定し、movie_processを行う。

def main(args):
    if len(args) < 2 or len(args) > 3:
        print("動画ファイルのみを引数で指定してください。")
    elif len(args) == 2:
        target_file = args[1]
        if os.path.isfile(target_file):
            movie_process.movie_process(target_file)
        else:
            print("動画ファイルは存在しません.")
    elif len(args) == 3: # 1pか2pの指定
        target_file = args[1]
        player = args[2]
        if player != "1" and player != "2":
            print("playerの指定は半角の1か2で行なってください.")
            return
        if os.path.isfile(target_file):
            movie_process.movie_process(target_file, int(player))
        else:
            print("動画ファイルは存在しません.")

if __name__ == "__main__":
    args = sys.argv
    main(args)