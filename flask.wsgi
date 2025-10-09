import sys
import os

DIR=os.path.dirname(__file__)
sys.path.append(DIR)
#下のユーザ名やディレクトリ名は各自の好きなものに変更
sys.path.insert(0, '/home/mutotamaki/myapp/')

from flskauth import app as application

