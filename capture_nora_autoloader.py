from pathlib import Path
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


URL = "https://nora.ukl.uni-freiburg.de/godzilla/index.php"
USERNAME = "reisertm"
PASSWORD = "reseter"
OUT_DIR = Path("artifacts")
OUT_DIR.mkdir(exist_ok=True)


def click_first(page, selectors):
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count() > 0:
            try:
                locator.first.click(timeout=3000)
                return selector
            except Exception:
                continue
    return None


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1200})
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        page.screenshot(path=str(OUT_DIR / "nora-login-page.png"), full_page=True)

        user_selectors = [
            'input[name="user"]',
            'input[name="username"]',
            'input[type="text"]',
            'input[placeholder*="user" i]',
            'input[placeholder*="login" i]',
        ]
        pass_selectors = [
            'input[name="pwd"]',
            'input[name="password"]',
            'input[type="password"]',
        ]

        for selector in user_selectors:
            loc = page.locator(selector)
            if loc.count() > 0:
                loc.first.fill(USERNAME)
                break
        else:
            raise RuntimeError("Could not find username input")

        for selector in pass_selectors:
            loc = page.locator(selector)
            if loc.count() > 0:
                loc.first.fill(PASSWORD)
                break
        else:
            raise RuntimeError("Could not find password input")

        clicked = click_first(
            page,
            [
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'input[type="submit"]',
                'text=/^login$/i',
            ],
        )
        if not clicked:
            page.keyboard.press("Enter")

        page.wait_for_timeout(5000)
        page.screenshot(path=str(OUT_DIR / "nora-after-login-5s.png"), full_page=True)
        page.wait_for_timeout(10000)
        page.screenshot(path=str(OUT_DIR / "nora-after-login-15s.png"), full_page=True)
        page.wait_for_timeout(15000)
        page.screenshot(path=str(OUT_DIR / "nora-after-login-30s.png"), full_page=True)
        (OUT_DIR / "nora-page-title.txt").write_text(page.title(), encoding="utf-8")
        (OUT_DIR / "nora-page-url.txt").write_text(page.url, encoding="utf-8")
        (OUT_DIR / "nora-after-login.html").write_text(page.content(), encoding="utf-8")

        click_first(
            page,
            [
                'text=/autoload/i',
                'button:has-text("Autoloader")',
                '[title*="autoload" i]',
                '[aria-label*="autoload" i]',
                '.toolbutton[title*="autoload" i]',
            ],
        )

        try:
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeoutError:
            pass

        clipped = False
        headings = page.locator("h2.KFormTitle").all()
        for heading in headings:
            try:
                text = heading.inner_text().strip().lower()
            except Exception:
                continue
            if text != "autoloaders":
                continue
            try:
                dialog = heading.evaluate_handle("node => node.closest('.dialog_generic_frame') || node.parentElement")
                dialog.as_element().screenshot(path=str(OUT_DIR / "nora-autoloader-pane.png"))
                clipped = True
                break
            except Exception:
                continue

        if not clipped:
            page.screenshot(path=str(OUT_DIR / "nora-autoloader-pane.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
