from pathlib import Path
from playwright.sync_api import sync_playwright


URL = "https://nora.ukl.uni-freiburg.de/godzilla/index.php"
USERNAME = "reisertm"
PASSWORD = "reseter"
OUT = Path("artifacts/autoloader-introspection.txt")
OUT.parent.mkdir(exist_ok=True)


def fill_first(page, selectors, value):
    for selector in selectors:
        loc = page.locator(selector)
        if loc.count() > 0:
            loc.first.fill(value)
            return True
    return False


def click_first(page, selectors):
    for selector in selectors:
        loc = page.locator(selector)
        if loc.count() > 0:
            try:
                loc.first.click(timeout=3000)
                return True
            except Exception:
                continue
    return False


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1200})
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        assert fill_first(page, ['input[name="username"]', 'input[name="user"]', 'input[type="text"]'], USERNAME)
        assert fill_first(page, ['input[name="password"]', 'input[name="pwd"]', 'input[type="password"]'], PASSWORD)
        if not click_first(page, ['button:has-text("Login")', 'input[type="submit"]', 'text=/^login$/i']):
            page.keyboard.press("Enter")

        page.wait_for_timeout(25000)

        data = page.evaluate(
            """() => {
                const result = {};
                result.title = document.title;
                result.url = location.href;
                result.formTitles = Array.from(document.querySelectorAll('h2.KFormTitle')).map(n => n.textContent.trim()).filter(Boolean);
                result.tabs = Array.from(document.querySelectorAll('.KListItem a, .menu_generic a')).map(n => n.textContent.trim()).filter(Boolean);
                const autoTitle = Array.from(document.querySelectorAll('h2.KFormTitle')).find(n => n.textContent.trim() === 'Autoloaders');
                if (!autoTitle) return result;
                const dialog = autoTitle.closest('.dialog_generic_frame') || autoTitle.parentElement;
                result.dialogText = dialog ? dialog.innerText : '';
                result.checkboxNames = dialog ? Array.from(dialog.querySelectorAll('input[type="checkbox"]')).map(n => n.name) : [];
                result.inputNames = dialog ? Array.from(dialog.querySelectorAll('input')).map(n => n.name) : [];
                result.selectNames = dialog ? Array.from(dialog.querySelectorAll('select')).map(n => n.parentElement?.getAttribute('name') || '') : [];
                result.buttonLabels = dialog ? Array.from(dialog.querySelectorAll('.modernbutton, .KFormItem_formarray_tool')).map(n => n.textContent.trim()).filter(Boolean) : [];
                return result;
            }"""
        )

        lines = []
        for key, value in data.items():
            lines.append(f"## {key}")
            lines.append(str(value))
            lines.append("")
        OUT.write_text("\n".join(lines), encoding="utf-8")
        browser.close()


if __name__ == "__main__":
    main()
