#!/usr/bin/env python3
"""Builds the looping product clips under media/ from real app screen recordings.

The site shows the app at work instead of a mock: every frame comes from an
unedited screen recording made by the app repo's capture tools. Only waits are
cut out, and every cut lands on a pair of identical frames, so the edit is
invisible. Each loop ends with a short cross-fade back into its own first
frame, so it repeats without a seam.

Sources (in the Cognito app repository, aso/motion/out/):
  study-loop/take8/screen.mov  iPhone 18 Pro simulator, iOS 27, 402 x 874 pt at 3x,
                               -ui-testing-seed-screenshots -ui-testing-study-loop-cards
  mac/take6/screen.mov         Cognito for Mac, 1280 x 840 pt screen rect at 2x,
                               -mac-marketing-capture (offline sample library and
                               a prepared generation result, so AI wording varies)

usage: tools/make_media.py [path to the Cognito repo]   (default: ../Cognito)
Needs ffmpeg with libx264 and Pillow with WebP.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'Cognito')
OUT = os.path.join(ROOT, 'media')
FADE = 0.4

CLIPS = {
    # Home -> Daily Mix -> reveal, Good -> reveal, Again -> reveal, Easy -> reveal ->
    # last card, Good -> session result.
    'study-iphone': {
        'src': 'aso/motion/out/study-loop/take8/screen.mov',
        'size': (780, 1696),
        # The simulator tags its frames Display P3, but the pixel values are the app's
        # sRGB colours (they match app-home.webp), so they pass through unconverted.
        'pre': 'null',
        # Cuts sit inside still stretches (frame timestamps checked with ffprobe),
        # and the jump from card 3 to card 6 is between two revealed answers.
        'segments': [(21.0, 22.3), (26.1, 28.2), (30.1, 31.6), (34.0, 36.1), (36.8, 38.3),
                     (40.9, 43.1), (43.8, 45.3), (47.8, 50.1), (50.8, 52.3), (73.4, 77.6)],
    },
    # Create Cards: paste notes -> Create -> preview -> Save 6 cards into Cell Biology.
    'create-mac': {
        'src': 'aso/motion/out/mac/take6/screen.mov',
        'size': (1280, 896),
        # The Create Cards window: 1199 x 840 pt from the top-left of the capture.
        'pre': 'crop=2398:1680:0:0',
        'segments': [(10.9, 12.6), (15.0, 17.2), (21.9, 23.6), (23.9, 25.6), (25.8, 27.6)],
    },
}


def build(name, clip):
    src = os.path.join(APP, clip['src'])
    w, h = clip['size']
    segs = clip['segments']
    end = max(b for _, b in segs) + 1
    # One input, made constant-rate from its first frame before any cut: the
    # simulator only writes a frame when the screen changes, so seeking into a
    # still stretch would land on the next change instead of the requested time.
    args = ['ffmpeg', '-v', 'error', '-y', '-t', f'{end:.3f}', '-i', src]
    n = len(segs) + 1
    graph = [f"[0:v]fps=30,{clip['pre']},scale={w}:{h}:flags=lanczos,setsar=1,format=yuv420p,"
             f"split={n}" + ''.join(f'[c{i}]' for i in range(n))]
    a0 = segs[0][0]
    for i, (a, b) in enumerate(segs + [(a0, a0 + FADE)]):
        graph.append(f'[c{i}]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,settb=1/30[s{i}]')
    graph.append(''.join(f'[s{i}]' for i in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0,settb=1/30[body]')
    total = sum(b - a for a, b in segs)
    graph.append(f'[body][s{len(segs)}]xfade=transition=fade:duration={FADE}:offset={total - FADE:.3f}[v]')

    mp4 = os.path.join(OUT, f'{name}.mp4')
    args += ['-filter_complex', ';'.join(graph), '-map', '[v]', '-an',
             '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '25', '-tune', 'animation',
             '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-color_primaries', 'bt709', '-color_trc', 'iec61966-2-1', '-colorspace', 'bt709',
             '-movflags', '+faststart', mp4]
    subprocess.run(args, check=True)

    # The poster is the clip's own first frame, so starting playback never jumps.
    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, 'poster.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-frames:v', '1', png], check=True)
        Image.open(png).convert('RGB').save(os.path.join(OUT, f'{name}.webp'), quality=88, method=6)
    print(f'{name}: {total:.1f}s, {os.path.getsize(mp4) / 1e6:.2f} MB')


os.makedirs(OUT, exist_ok=True)
for name, clip in CLIPS.items():
    build(name, clip)
