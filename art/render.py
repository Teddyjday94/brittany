import sys
from playwright.sync_api import sync_playwright
src,out,scale=sys.argv[1],sys.argv[2],float(sys.argv[3])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':1600},device_scale_factor=scale)
    pg.goto('file://'+src); pg.wait_for_timeout(500)
    pg.locator('#p').screenshot(path=out); b.close()
