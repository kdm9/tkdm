#!/usr/bin/env python3
# Copyright (c) 2022 Dr. K. D. Murray/Gekkonid Consulting <spam@gekkonid.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
from tqdm import tqdm
try:
    import HeifImagePlugin
except ImportError:
    print("Failed to load HeifImagePlugin. *.HEIF won't be supported.", file=stderr)

import argparse
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import os
from sys import stderr

@dataclass
class RenderedImg:
    filename: str
    relimgpath: str
    relthumbpath: str

@dataclass
class RenderedSubdir:
    name: str
    images: list[RenderedImg]

def render_subdir(dirpath, outbase):
    dirname = Path(dirpath).name

    outpath= Path(outbase) / dirname
    outpath.mkdir(exist_ok=True, parents=True)

    res = RenderedSubdir(dirname, [])
    for root, _, files in os.walk(dirpath):
        for file in files:
            file = Path(root) / file
            try:
                img = Image.open(file)
                img.load()
            except IOError as exc:
                print(str(exc), file=stderr)
                continue
            fname = (file.stem+".jpg")
            img.save(outpath / fname)

            tname = (file.stem+".thumb.jpg")
            img.thumbnail((320, 240))
            img.save(outpath / tname)
            res.images.append(RenderedImg(file.name, f"{dirname}/{fname}", f"{dirname}/{tname}"))
        break
    return res

DOC="""
autogallery expects that you have images either in a single input dir, or in only one layer of directories. For example, either of the following is supported:

    inputdir/
        a/
            img1.jpg
            img2.jpg
        b/
            img3.jpg
            img4.jpg
        img5

OR
    inputdir/
        img1.jpg
        img2.jpg

Any images that are in directories deeper than one level lower than the input directory will be silently ignored.
"""

def main(argv=None):
    """Generate HTML image galleries"""
    ap = argparse.ArgumentParser(epilog=DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", type=Path, required=True,
            help="Output base directory")
    ap.add_argument("-i", "--indir", type=Path, required=True,
            help="Input base directory")
    ap.add_argument("-t", "--threads", default=1, type=int,
            help="parallel threads")
    args = ap.parse_args(argv)

    outpath = args.outdir
    outpath.mkdir(exist_ok=True)

    res = []
    jobs = []
    with ProcessPoolExecutor(args.threads) as exc:

        for root, dirs, files in os.walk(args.indir):
            root = Path(root)
            jobs.append(exc.submit(render_subdir, root/".", outpath))
            for dir in dirs:
                jobs.append(exc.submit(render_subdir, root/dir, outpath))
            break

        for job in tqdm(as_completed(jobs), total=len(jobs)):
            res.append(job.result())

    divid = 0
    with open(outpath / "index.html", "w") as fh:
        body = []
        for dir in sorted(res, key=lambda d: d.name):
            divid += 1
            imgs = []
            for img in dir.images:
                imgs.append(f"""
                    <a href="{img.relimgpath}" itemprop="contentUrl" title="{img.filename}" data-lightbox="global">
                        <img itemprop="thumbnail" src="{img.relthumbpath}" alt="{img.filename}" />
                    </a>
                    """)
            imgs = "\n".join(imgs)
            div=f"""
            <h1>{dir.name}</h1>
            <div id="dirdiv{divid}" itemscope itemtype="http://schema.org/ImageGallery">
              {imgs}
            </div>
            <script>
                $("#dirdiv{divid}").justifiedGallery({{
                    rowHeight: 240,
                    lastRow: "left",
                }});
            </script>
            """
            body.append(div)
        body = "\n".join(body)
        fh.write(f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{args.indir.name}</title>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/justifiedGallery@3.8.1/dist/js/jquery.justifiedGallery.min.js" integrity="sha256-sv0FpYm7s9wU5OAD8AzZGhVXlvKBUQvjoJjL435kS1o=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/lightbox2@2.11.4/dist/js/lightbox.min.js" integrity="sha256-TDAA/HYea7i2C/VZwZ7kw0mTTUAoDVup9sMJ9KlVhbs=" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lightbox2@2.11.4/dist/css/lightbox.min.css" integrity="sha256-tBxlolRHP9uMsEFKVk+hk//ekOlXOixLKvye5W2WR5c=" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/justifiedGallery@3.8.1/dist/css/justifiedGallery.min.css" integrity="sha256-YBy2rK4TkyaeKbMYUy56/rUERtR7sMEmkQvDr9EuHUQ=" crossorigin="anonymous">
  </head>
  <body>
  {body}
  </body>
</html>
""")
        
if __name__ == "__main__":
    main()
