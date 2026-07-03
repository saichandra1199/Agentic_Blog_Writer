import re
import time
from pathlib import Path

import markdown
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from state import BlogState

PROFILE_DIR = Path.home() / ".medium_uc_profile"

# JS: simulate a real paste event with HTML data so Quill processes it properly
_PASTE_JS = """
(function(html) {
    var editor = document.querySelector('.postArticle-content.js-postField') ||
                 document.querySelector('[contenteditable]');
    if (!editor) return 'no editor';
    editor.focus();
    var dt = new DataTransfer();
    dt.setData('text/html', html);
    dt.setData('text/plain', editor.innerText);
    var ev = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
    editor.dispatchEvent(ev);
    return 'ok';
})(arguments[0]);
"""


def _md_to_html(md_content: str) -> str:
    """Markdown → HTML, stripping local image refs, keeping remote URLs."""
    # Drop local image refs
    text = re.sub(r'!\[.*?\]\((?!https?://).*?\)', '', md_content)
    # Strip HTML comments (unresolved placeholders)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def publish_to_medium(state: BlogState) -> BlogState:
    PROFILE_DIR.mkdir(exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    driver = uc.Chrome(options=options, use_subprocess=True)

    try:
        driver.get("https://medium.com/new-story")
        time.sleep(3)

        if "medium.com/new-story" not in driver.current_url:
            print("\n🔐 Log in to Medium in the browser window, then press Enter here...")
            input("Press Enter after logging in: ")
            driver.get("https://medium.com/new-story")
            time.sleep(3)
            print("✅ Session saved to profile (won't ask again).")

        print("\n⏳ Complete any CAPTCHA/verification in the browser.")
        print("   Press Enter here ONLY when the blank story editor is visible.")
        input("Press Enter when editor is ready: ")

        # Find editor elements
        editables = driver.find_elements(By.CSS_SELECTOR, "[contenteditable]")
        if not editables:
            print(f"⚠️  No editable elements found. URL: {driver.current_url}")
            input("Press Enter to close: ")
            return {**state, "medium_url": None}

        # Focus main editor
        editor = editables[0]
        driver.execute_script("arguments[0].click(); arguments[0].focus();", editor)
        time.sleep(0.5)

        # Type title into the title field
        title_el = driver.find_elements(By.CSS_SELECTOR, ".graf--title, p.graf:first-of-type")
        if title_el:
            driver.execute_script("arguments[0].focus();", title_el[0])
            title_el[0].send_keys(state["title"])
        else:
            driver.switch_to.active_element.send_keys(state["title"])

        # Move to body — click below title area
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        time.sleep(0.5)

        # Simulate paste event with HTML — Quill processes this into rich formatting
        html_content = _md_to_html(state.get("final_blog", ""))
        result = driver.execute_script(_PASTE_JS, html_content)
        print(f"\n🔧 Paste result: {result}")
        time.sleep(2)

        seo = state.get("seo_data") or {}
        tags = seo.get("tags", [])
        print("\n📝 Blog loaded in Medium editor.")
        if tags:
            print(f"   Suggested tags: {', '.join(tags[:5])}")
        print("   Add tags, review, then publish manually in the browser.")
        print("\nPress Enter to close the browser...")
        input()

    finally:
        driver.quit()

    return {**state, "medium_url": "published"}
