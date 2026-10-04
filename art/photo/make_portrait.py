"""Builds portrait.webp: a sticker cutout of the CC BY 3.0 still (Sarah Baska, 2021) for the home hero.
Inputs: broski-crop-source.jpg plus two rembg cutouts (isnet-general-use keeps the sunglasses,
u2net_human_seg keeps the hand). Run from the repo root: python3 art/photo/make_portrait.py"""
from PIL import Image, ImageChops, ImageFilter
D = "art/photo/"
src = Image.open(D + "broski-crop-source.jpg").convert("RGBA")
m = ImageChops.lighter(Image.open(D + "mask-isnet.png").getchannel("A"), Image.open(D + "mask-human.png").getchannel("A"))
m = m.point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.MedianFilter(9))
W, H = src.size; P = 40
# pad so the outline wraps the sides and top but the flat bottom edge stays flat
big = Image.new("L", (W + 2 * P, H + 2 * P), 0); big.paste(m, (P, P))
for y in range(H + P, H + 2 * P):           # extend the bottom row downward
    big.paste(m.crop((0, H - 1, W, H)), (P, y))
def grow(mask, r): return mask.filter(ImageFilter.MaxFilter(r * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
cream, ink = grow(big, 9), grow(big, 15)
out = Image.new("RGBA", big.size, (0, 0, 0, 0))
out.paste((36, 8, 46, 255), (0, 0), ink)
out.paste((255, 244, 226, 255), (0, 0), cream)
body = src.copy(); body.putalpha(m.filter(ImageFilter.GaussianBlur(1.1)))
out.alpha_composite(body, (P, P))
out = out.crop((0, 0, W + 2 * P, H + P))    # drop the padded bottom
out.save("portrait.webp", quality=86, method=6)
print(out.size)
