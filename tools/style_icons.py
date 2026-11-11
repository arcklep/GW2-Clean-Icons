"""style_icons.py: the Soft, Cold and Dark styles of GW2 Clean Squares, after Simpy's IconPacks for World of Warcraft
(github.com/kodewdle/IconPacks).
Soft: each square shrunk to the game's own 64 px (which drops the grain laid back on the pack), upscaled 4x by
Real-ESRGAN's anime model (realesrgan-ncnn-vulkan -n realesrgan-x4plus-anime -s 4) for smooth fills and clean outlines,
and brought back to 128 px with the original's alpha and broad colour (its blur put back under the upscale's detail). Cold and Dark: colour grades of Soft fitted to Simpy's Cold and
Dark previews against his Clean one (a degree-3 polynomial in R, G, B, then a square edge shade; 3/255 mean error on
the preview icons).

python tools/style_icons.py prep <icons_square> <dir of 64 px inputs>       (then run Real-ESRGAN on it)
python tools/style_icons.py <icons_square> <Real-ESRGAN output dir> <out dir> soft|cold|dark
"""
import os
import sys

import numpy as np
from PIL import Image



def uniform_filter(x, k):
    """Mean over a k x k box (edges padded by reflection)."""
    r = k // 2
    p = np.pad(x, r, mode="reflect")
    c = np.cumsum(np.cumsum(p, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    h, w = x.shape
    return (c[k:k + h, k:k + w] - c[0:h, k:k + w] - c[k:k + h, 0:w] + c[0:h, 0:w]) / (k * k)

def gaussian_filter(x, s):
    # three box passes approximate a Gaussian
    k = max(1, int(round(s * 1.7))) | 1
    for _ in range(3):
        x = uniform_filter(x, k)
    return x

def guided(I, p, r, eps):
    k = 2 * r + 1
    mI = uniform_filter(I, k); mp = uniform_filter(p, k)
    cov = uniform_filter(I * p, k) - mI * mp
    var = uniform_filter(I * I, k) - mI * mI
    a = cov / (var + eps); b = mp - a * mI
    return uniform_filter(a, k) * I + uniform_filter(b, k)

def soften(img, r=2, eps=0.004, passes=2, sharpen=0.35):
    """img: HxWx3 (or 4) in 0..1, 128 px. Returns the soft version (alpha kept)."""
    rgb = img[..., :3].copy()
    for _ in range(passes):
        y = rgb @ np.array([0.2126, 0.7152, 0.0722])
        rgb = np.stack([guided(y, rgb[..., c], r, eps) for c in range(3)], -1)
    blur = np.stack([gaussian_filter(rgb[..., c], 2.0) for c in range(3)], -1)
    rgb = np.clip(rgb + sharpen * (rgb - blur), 0, 1)
    if img.shape[-1] == 4:
        return np.concatenate([rgb, img[..., 3:]], -1)
    return rgb


GRADES = {"cold": {"coef": [[0.008372789806622948, 0.01233553437732612, 0.011344377871147645], [0.8688159026974406, 0.26505556097557326, 0.2667862174726142], [0.04702365983525661, 0.6124541527110298, 0.050663968672366985], [-0.00044397976439420044, 0.059543827842123316, 0.5843288499056287], [0.42073456848838764, 0.07909842452922242, 0.20034033913753868], [0.4841403527621321, 0.8558065237433611, 0.5268531104391123], [0.8799794500244905, 0.4948268869793978, 0.9460701290704051], [-0.5511672530206511, -0.5934408064335309, -0.4918170231392992], [-1.0398413783499687, -0.489718501561688, -0.7703693640837391], [0.0445498569065983, -0.21561673790638075, -0.12943575980886848], [-0.30253885599972974, 0.03532113491794858, -0.09083818170043316], [-0.024007459260463205, -0.2282524081064629, 0.024691669461219666], [0.10131284393845127, 0.2814947928767377, -0.19650127942380374], [0.4914536162415054, 0.07047360366499043, 0.4796641246355687], [1.1216061985709052, 0.43757718081791686, 0.28345559759872496], [-0.44626176402059503, -0.10954861328307003, -0.5976473642998958], [0.2096336110104321, -0.35686673524099277, 0.185097862380116], [-0.9883792396761512, -0.8198176141705196, -0.19777764233079959], [-0.05564239593988105, -0.07334973112054383, -0.34806564683248187], [-0.2573814907916567, 0.6972894119275505, 0.2772386494294632]], "shade": [0.9980700203466599, 0.9985021523975708, 0.9948778839615553, 0.9959265971592023, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9967631436019665, 0.9945964751285838, 0.9933187417586954, 0.9928341292176585, 0.9927864293976535, 0.9928116808729844]}, "dark": {"coef": [[0.004789720343819167, 0.000582658796179542, 0.0034700998984132855], [0.8357326154467546, 0.015365889835725908, -0.0041325300602061705], [-0.008027652630666793, 0.8268324562405602, -0.040681219566389974], [-0.004426562875503016, -0.0024356330002202526, 0.8489573193424976], [-0.09293102298275968, -0.061421302867301075, -0.005764220890947948], [-0.008580372062194606, -0.06306572012617415, 0.04655561402190325], [0.16331997656092198, 0.019428713782321333, 0.0590354004830314], [0.02682404262565439, 0.04571360253646852, 0.08887618834270566], [-0.1492645890975231, -0.027476274270734825, -0.12251666108121262], [0.024424618000976187, 0.008047009104674383, -0.05107927283932791], [0.06279766617508346, 0.049238225077936376, 0.006808542565950993], [0.024170783695347694, -0.002591671855335503, -0.009685856943152235], [-0.09791957681948513, 0.0003390912300500418, -0.022759220979219143], [0.04373433572226792, -0.06567424596262653, -0.04212809851674471], [-0.06751192660321964, 0.069899080644151, 0.04489439490513399], [-0.055880056784907615, 0.07744372256654428, -0.043163325578318146], [0.00398543851170021, 0.13714389821288886, -0.0007803138051365121], [0.12708972683770176, -0.020276201198763624, -0.016761239081562646], [-0.13966186317151227, 0.013416987411154938, 0.017131190745500614], [0.12148625274043966, -0.20585699309968142, 0.05736631687617948]], "shade": [0.9889460008512639, 0.9887948803361684, 0.9938235013156548, 0.9956736376342521, 0.9933748630483975, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9950221592259747, 0.9467101171235699, 0.8748381653212935, 0.7795496760398815, 0.6569816248871859, 0.5340339065391352, 0.44665812032555835]}}


def radius(h):
    yy, xx = np.mgrid[0:h, 0:h]
    c = (h - 1) / 2
    return np.maximum(abs(xx - c), abs(yy - c)) / c


def feats(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    t = [np.ones_like(r), r, g, b, r*r, g*g, b*b, r*g, r*b, g*b, r*r*r, g*g*g, b*b*b, r*r*g, r*r*b, g*g*r, g*g*b, b*b*r, b*b*g, r*g*b]
    return np.stack(t, -1)


def grade(rgb, style):
    g = GRADES[style]
    out = feats(rgb) @ np.array(g["coef"])
    s = np.interp(radius(rgb.shape[0]), np.linspace(0, 1, len(g["shade"])), g["shade"])
    return np.clip(out * s[..., None], 0, 1)


SOFT = dict(r=3, eps=0.01, passes=2, sharpen=0.25)


def style_image(img, style, upscaled=None):
    """upscaled: Real-ESRGAN's 4x of the 64 px icon (RGBA 0..1); without it, the edge-preserving smooth below."""
    if upscaled is not None:
        # the upscale's detail and outlines, the original's broad colour and brightness (the anime model darkens and
        # adds contrast): upscaled - blur(upscaled) + blur(original)
        def blur(x):
            return np.stack([gaussian_filter(x[..., c], 4.0) for c in range(3)], -1)
        rgb = np.clip(upscaled[..., :3] - blur(upscaled[..., :3]) + blur(img[..., :3]), 0, 1)
        a = np.concatenate([rgb, img[..., 3:]], -1)
    else:
        a = soften(img, **SOFT)
    if style != "soft":
        a = np.concatenate([grade(a[..., :3], style), a[..., 3:]], -1)
    return a


def main():
    if sys.argv[1] == "prep":
        os.makedirs(sys.argv[3], exist_ok=True)
        for f in sorted(os.listdir(sys.argv[2])):
            if f.endswith(".png"):
                Image.open(os.path.join(sys.argv[2], f)).convert("RGBA").resize((64, 64), Image.LANCZOS).save(os.path.join(sys.argv[3], f))
        return
    src, up, dst, style = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not f.endswith(".png"):
            continue
        im = Image.open(os.path.join(src, f)).convert("RGBA")
        a = np.asarray(im).astype(float) / 255
        u = Image.open(os.path.join(up, f)).convert("RGBA").resize(im.size, Image.LANCZOS)
        out = style_image(a, style, np.asarray(u).astype(float) / 255)
        Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(dst, f), optimize=True)


if __name__ == "__main__":
    main()
