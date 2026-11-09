"""Turns the boon and condition badges (the orange "house" boons, the red shield conditions, and the trait
buffs drawn in the same badges) into plain squares: the badge's own background colour fills the square and
the symbol is centred, like the skill icons.

Run from the repository root: python tools/square_effects.py
Reads icons_square/<id>.png (the shaped originals) and writes:
  icons_square/<id>.png  square corners
  icons/<id>.png         the skill icons' rounded corners
An icon that is already square (fully opaque) is skipped, so running it twice changes nothing.
"""
import os, numpy as np
from collections import deque
from PIL import Image, ImageFilter
N=128
yy,xx=np.mgrid[0:N,0:N]/(N-1)*2-1
def basis(y,x): return np.stack([np.ones_like(x),x,y,x*y,x*x,y*y],-1)
B=basis(yy,xx)

def gblur(x, s):
    r=int(3*s); k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
    y=np.pad(x,[(r,r),(r,r)]+[(0,0)]*(x.ndim-2),mode='edge')
    y=np.apply_along_axis(lambda v: np.convolve(v,k,'valid'),0,y)
    return np.apply_along_axis(lambda v: np.convolve(v,k,'valid'),1,y)

def fit(rgb, m):
    A=B[m]; c,*_=np.linalg.lstsq(A, rgb[m], rcond=None)
    return np.clip(B@c,0,1)

def fill_field(rgb, w, s):
    return gblur(rgb*w[...,None], s)/np.maximum(gblur(w, s),1e-9)[...,None]

def components(mask):
    lab=np.zeros(mask.shape,int); comps=[]
    for sy,sx in zip(*np.nonzero(mask)):
        if lab[sy,sx]: continue
        n=len(comps)+1; q=deque([(sy,sx)]); lab[sy,sx]=n; pts=[]
        while q:
            y,x=q.popleft(); pts.append((y,x))
            for ny,nx in ((y+1,x),(y-1,x),(y,x+1),(y,x-1)):
                if 0<=ny<N and 0<=nx<N and mask[ny,nx] and not lab[ny,nx]:
                    lab[ny,nx]=n; q.append((ny,nx))
        comps.append(np.array(pts))
    return comps

def squarify(im, erode=7):
    a=np.array(im.convert('RGBA')).astype(np.float64)/255
    rgb, al = a[...,:3], a[...,3]
    P=24
    sm=np.pad(((al>0.5)*255).astype(np.uint8),P)
    shape=Image.fromarray(sm)
    inner=(np.array(shape.filter(ImageFilter.MinFilter(2*erode+1)))>0)[P:-P,P:-P]
    core=(np.array(shape.filter(ImageFilter.MinFilter(2*(erode+6)+1)))>0)[P:-P,P:-P]
    ring=inner & ~(np.array(Image.fromarray(np.pad((inner*255).astype(np.uint8),P)).filter(ImageFilter.MinFilter(9)))[P:-P,P:-P]>0)
    med=np.median(rgb[ring],0)
    bg=inner & (np.sqrt(((rgb-med)**2).sum(-1))<0.25)
    for it in range(4):
        field=fit(rgb,bg)
        d=np.sqrt(((rgb-field)**2).sum(-1))
        bg=inner & (d<(0.16 if it<3 else 0.12))
    sym=inner & ~bg
    sym=np.array(Image.fromarray((sym*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3)))>0
    # drop rim remnants: components that never reach the core of the shape
    keep=np.zeros_like(sym)
    for c in components(sym):
        if len(c)<6: continue
        if core[c[:,0],c[:,1]].mean()>0.25: keep[c[:,0],c[:,1]]=True
    sym=keep
    # background: smooth fit + synthetic grit at the original's level
    res=(rgb-field)[bg]; sd=res.std(0)
    rng=np.random.default_rng(int(rgb.sum()*1000)%2**32)
    noise=gblur(rng.normal(0,1,(N,N)),0.8); noise/=noise.std()
    # extend the fit beyond the old shape smoothly instead of extrapolating the polynomial
    ext=field.copy()
    for sg in (3,6,12,24):
        e=fill_field(field, inner.astype(np.float64), sg)
        ext=np.where(inner[...,None], field, e if sg==3 else np.where(np.isfinite(ext),ext,e))
    w=gblur(inner.astype(np.float64),3)[...,None]
    field_full=field*w+fill_field(field, inner.astype(np.float64), 10)*(1-w)
    field_full=np.where(inner[...,None], field, field_full)
    field_full=gblur(field_full,2)
    base=np.clip(field_full+noise[...,None]*sd*0.85,0,1)
    ys,xs=np.nonzero(sym)
    cy=(ys.min()+ys.max())/2; cx=(xs.min()+xs.max())/2
    dy=int(round((N-1)/2-cy)); dx=int(round((N-1)/2-cx))
    reg=np.array(Image.fromarray((sym*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))/255.0
    reg=gblur(reg,0.8)*inner
    sh=lambda x: np.roll(np.roll(x,dy,0),dx,1)
    m=np.clip(sh(reg)*1.3,0,1)[...,None]
    symc=np.clip(sh(rgb-field)+base,0,1)
    out=base*(1-m)+symc*m
    return Image.fromarray((np.clip(out,0,1)*255+0.5).astype(np.uint8),'RGB').convert('RGBA'), (dy,dx)

IDS = '''
1012402 1012410 1012443 1012479 1012570 1012573 1012670 1012682 1012684 1012697
1012698 1012835 102834 102835 102836 102837 102838 102839 102840 102842
102843 102844 102848 102849 102850 102852 102853 102854 102869 102880
1228472 1466322 1938787 2128013 2128014 2128015 2128016 2440718 415959 514400
514408 598887 961397 961398
'''.split()


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND_FROM = '102965'   # any skill icon: they all share the same rounded-corner alpha

def main():
    rounded = np.array(Image.open(os.path.join(ROOT, 'icons', ROUND_FROM + '.png')).convert('RGBA'))[..., 3]
    rounded[16:-16, :] = 255; rounded[:, 16:-16] = 255
    done = 0
    for i in IDS:
        p = os.path.join(ROOT, 'icons_square', i + '.png')
        im = Image.open(p).convert('RGBA')
        if np.array(im)[..., 3].min() == 255:
            continue
        sq, _ = squarify(im)
        sq.save(p, optimize=True)
        r = np.array(sq); r[..., 3] = rounded
        Image.fromarray(r, 'RGBA').save(os.path.join(ROOT, 'icons', i + '.png'), optimize=True)
        done += 1
    print(done, 'of', len(IDS), 'icons squared')

if __name__ == '__main__':
    main()
