"""Builds the 64 px set for Nameplate Scrolling Combat Text from the pack's icons/ (rounded ones, not icons_square).

Run from the repository root: python nameplate-sct-64/make.py
Writes nameplate-sct-64/icons/<file id>.png (64 x 64, 256-colour palette with alpha), copies skills.json and
effect_ids.json beside them, and builds Nameplate-SCT-Icons-64.zip (stored, not deflated: the PNGs are already
compressed, and the addon unpacks it without a zlib).
"""
import glob, json, os, shutil, zipfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'nameplate-sct-64')
SIZE = 64

def main():
    icons = os.path.join(OUT, 'icons')
    os.makedirs(icons, exist_ok=True)
    files = sorted(glob.glob(os.path.join(ROOT, 'icons', '*.png')))
    for f in files:
        im = Image.open(f).convert('RGBA').resize((SIZE, SIZE), Image.LANCZOS)
        im.quantize(256, method=Image.Quantize.FASTOCTREE).save(os.path.join(icons, os.path.basename(f)), 'PNG', optimize=True)
    for name in ('skills.json', 'effect_ids.json'):
        shutil.copyfile(os.path.join(ROOT, name), os.path.join(OUT, name))
    pack = json.load(open(os.path.join(ROOT, 'manifest.json')))
    manifest = {
        'name': 'GW2 Clean Icons, 64 px for Nameplate Scrolling Combat Text',
        'version': pack['version'],
        'icon_size': SIZE,
        'icons': len(files),
    }
    json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=2)
    zpath = os.path.join(ROOT, 'Nameplate-SCT-Icons-64.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_STORED) as z:
        for name in ('manifest.json', 'skills.json', 'effect_ids.json', 'README.md'):
            z.write(os.path.join(OUT, name), name)
        for f in sorted(os.listdir(icons)):
            z.write(os.path.join(icons, f), 'icons/' + f)
    print(len(files), 'icons;', os.path.getsize(zpath) // 1024, 'KB zip')

if __name__ == '__main__':
    main()
