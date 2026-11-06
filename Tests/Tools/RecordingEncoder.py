"""Test-only encoder proxy; generate an executable launcher with an absolute Python shebang.

The adjacent <launcher>.json selects mode, marker and qualified FFmpeg. No runtime
package uses Python. The blocking fixture has no child process of its own.
"""
from pathlib import Path
import json, os, subprocess, sys, time
config = json.loads(Path(sys.argv[0] + '.json').read_text())
mode = config['mode']
if sys.argv[1:] == ['-version']:
    if mode == 'probe-block':
        Path(config['marker']).write_text(str(os.getpid()))
        time.sleep(60)
    print('other program' if mode == 'wrong-banner' else 'ffmpeg version recording-fixture')
    sys.exit(0)
if mode == 'error':
    sys.stderr.write('deliberate encoder failure\n')
    sys.exit(7)
if mode == 'flood':
    sys.stderr.write('deliberate diagnostic flood\n' * 10000)
    sys.exit(7)
if mode == 'empty':
    Path('movie.mp4').touch()
    sys.exit(0)
if mode == 'blocked':
    assert os.read(0, 1)
    Path(config['marker']).write_text(str(os.getpid()))
    time.sleep(60)
    sys.exit(9)
assert mode == 'slow'
args = sys.argv[1:]
width, height = map(int, args[args.index('-video_size') + 1].split('x'))
encoder = subprocess.Popen([config['ffmpeg'], *args], stdin=subprocess.PIPE)
Path(config['marker']).write_text(str(os.getpid()))
try:
    while True:
        image = bytearray()
        while len(image) < width * height * 4:
            chunk = os.read(0, width * height * 4 - len(image))
            if not chunk:
                break
            image.extend(chunk)
        if not image:
            break
        assert len(image) == width * height * 4
        time.sleep(0.08)
        encoder.stdin.write(image)
        encoder.stdin.flush()
    encoder.stdin.close()
    sys.exit(encoder.wait(timeout=30))
finally:
    if encoder.poll() is None:
        encoder.kill()
        encoder.wait()
