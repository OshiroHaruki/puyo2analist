import sys
import movie_process
import os

# 動画ファイルを実行時に引数で指定し、movie_processを行う。

def main(args):
    if len(args) != 2:
        print("動画ファイルのみを引数で指定してください。")
    else:
        target_file = args[1]
        if os.path.isfile(target_file):
            movie_process.movie_process(target_file)
        else:
            print("動画ファイルは存在しません.")

if __name__ == "__main__":
    args = sys.argv
    main(args)