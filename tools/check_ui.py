"""Optional: pip install playwright && python -m playwright install chromium."""
import sys
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from demo.server import Handler
from playwright.sync_api import sync_playwright


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    images = ROOT / 'docs' / 'images'
    images.mkdir(parents=True, exist_ok=True)
    errors = []
    states = 0
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width in (1920, 1440, 768, 390, 360):
                page = browser.new_page(viewport=dict(width=width, height=1000), device_scale_factor=1)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
                page.goto(f'http://127.0.0.1:{server.server_port}', wait_until='networkidle')
                page.locator('.game').first.wait_for()
                assert not page.locator('#error').is_visible()
                assert page.locator('.game-body > .probability').count() == 6
                assert page.locator('.game > .result').count() == 6
                for tab in ('prediction', 'statistics', 'operations'):
                    page.locator(f'[data-page="{tab}"]').click()
                    assert page.locator(f'#{tab}').is_visible()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, tab)
                    if tab == 'statistics':
                        page.locator('#weekday-tab').click()
                        assert page.locator('.chart-row').count() == 7
                        page.locator('#weekday-tab').press('ArrowLeft')
                        assert page.locator('#monthly-tab').get_attribute('aria-selected') == 'true'
                        assert page.locator('.chart-row').count() == 3
                        page.locator('#monthly-tab').blur()
                    if width == 1440 and tab in ('prediction', 'statistics'):
                        name = 'desktop' if tab == 'prediction' else 'statistics'
                        page.screenshot(path=str(images / f'demo-{name}.png'), full_page=True)
                    if width == 390 and tab == 'prediction':
                        page.screenshot(path=str(images / 'demo-mobile.png'), full_page=True)
                    states += 1
                page.close()
            browser.close()
        assert not errors, errors
        print(f'Passed {states} UI states; no browser errors or horizontal overflow.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    main()
