"""Headless browser QA of standalone HTML, print pagination and mobile overflow."""
import json
from pathlib import Path
import pymupdf
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def main():
    output=ROOT/'.cache/report_qa'
    output.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport={'width':1100,'height':1300},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto((ROOT/'report.html').as_uri(),wait_until='load')
        for i,element in enumerate(page.locator('article.page').all(),1):
            element.screenshot(path=str(output/f'screen_page_{i}.png'))
        page.emulate_media(media='print')
        overflow=page.locator('article.page').evaluate_all('(els)=>els.map(e=>({height:e.clientHeight,scrollHeight:e.scrollHeight,overflow:e.scrollHeight>e.clientHeight+2}))')
        # Tables scroll on screens; in print a hidden horizontal overflow silently drops columns.
        overflow+=page.locator('.table-scroll').evaluate_all('(els)=>els.map(e=>({width:e.clientWidth,scrollWidth:e.scrollWidth,overflow:e.scrollWidth>e.clientWidth+1}))')
        page.pdf(path=str(output/'report_print.pdf'),format='A4',print_background=True,prefer_css_page_size=True)
        page.emulate_media(media='screen')
        page.set_viewport_size({'width':375,'height':900})
        mobile=page.evaluate('({viewport:innerWidth,width:document.documentElement.scrollWidth})')
        page.screenshot(path=str(output/'mobile.png'),full_page=True)
        browser.close()
    document=pymupdf.open(output/'report_print.pdf')
    for i,pg in enumerate(document,1):
        pg.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(output/f'print_page_{i}.png')
    result={'pdf_pages':len(document),'print_overflow':overflow,'mobile':mobile,'browser_errors':errors}
    (output/'qa.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if len(document)!=2 or any(r['overflow'] for r in overflow) or mobile['width']>mobile['viewport'] or errors:
        raise SystemExit('Report QA failed; inspect renderings and fix layout.')


if __name__=='__main__':
    main()
