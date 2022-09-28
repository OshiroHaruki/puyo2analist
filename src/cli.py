import sys
import movie_process
import os
import movie_process_2p

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
    elif len(args) == 3: # とりあえずの分岐
        target_file = args[1]
        if os.path.isfile(target_file):
            movie_process_2p.movie_process_2p(target_file)
        else:
            print("動画ファイルは存在しません.")

if __name__ == "__main__":
    args = sys.argv
    main(args)