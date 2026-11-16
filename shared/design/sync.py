#!/usr/bin/env python3
"""tokens.css 를 HTML 파일들의 tokens:start ~ tokens:end 구간에 다시 넣는다.

쓰는 법 (저장소 루트에서):
  python3 shared/design/sync.py                 # 견본 3종 + 루트 index.html
  python3 shared/design/sync.py edu/apps/x/index.html   # 지정한 파일만
"""
import pathlib, re, sys

here = pathlib.Path(__file__).resolve().parent
root = here.parent.parent
css = (here / "tokens.css").read_text(encoding="utf-8").strip()
targets = [pathlib.Path(p) for p in sys.argv[1:]] or [
    here / "template-app.html", here / "template-dashboard.html",
    here / "template-guide.html", root / "index.html"]
pat = re.compile(r"(/\* tokens:start \*/).*?(/\* tokens:end \*/)", re.S)
for f in targets:
    s = f.read_text(encoding="utf-8")
    if not pat.search(s):
        print("표시 없음, 건너뜀:", f); continue
    f.write_text(pat.sub(lambda m: m.group(1) + "\n" + css + "\n" + m.group(2), s), encoding="utf-8")
    print("넣음:", f)
