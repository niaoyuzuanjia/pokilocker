import sys,os
r=r"d:\pokilocker"
os.chdir(r)
f=open(os.path.join(r,"b.txt"),"w",encoding="utf-8")
sys.stdout=f;sys.stderr=f
sys.argv[1:]=["--onefile","--windowed","--noupx","--name","PokiLocker","--add-data",r"d:\pokilocker\pokilocker;pokilocker","--hidden-import","qfluentwidgets","--noconfirm",r"d:\pokilocker\main.py"]
from PyInstaller.__main__ import run
run()
f.close()
sys.stdout=sys.__stdout__;sys.stderr=sys.__stderr__
e=os.path.join(r,"dist","PokiLocker.exe")
print(f"v{os.path.getsize(e)/1024/1024:.1f}MB" if os.path.exists(e) else "r2")
