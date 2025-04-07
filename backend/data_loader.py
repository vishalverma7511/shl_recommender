import asyncio
from playwright.async_api import async_playwright
import json
import os

BASE_URL = "https://www.shl.com"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "shl_catalog.json")

async def get_assessment_duration(page, url):
    await page.goto(url)
    try:
        duration_element = await page.query_selector("p:has-text('Duration:')")
        if duration_element:
            duration_text = await duration_element.inner_text()
            return duration_text.replace("Duration:", "").strip()
    except:
        return ""
    return ""

async def scrape_shl_catalog():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.shl.com/solutions/products/product-catalog/?type=2")

        results = []

        while True:
            rows = await page.query_selector_all("table tbody tr[data-course-id]")

            for row in rows:
                name_element = await row.query_selector("td a")
                name = await name_element.inner_text()
                relative_url = await name_element.get_attribute("href")
                full_url = BASE_URL + relative_url

                cols = await row.query_selector_all("td")

                remote_supported = "✔" if await cols[1].query_selector(".catalogue__circle.-yes") else "✘"
                adaptive_supported = "✔" if await cols[2].query_selector(".catalogue__circle.-yes") else "✘"

                test_type_elements = await cols[3].query_selector_all(".product-catalogue__key")
                test_types = [await el.inner_text() for el in test_type_elements]
                test_type_str = ", ".join(test_types)

                # Open a new page to get duration
                detail_page = await context.new_page()
                duration = await get_assessment_duration(detail_page, full_url)
                await detail_page.close()

                results.append({
                    "Assessment Name": name.strip(),
                    "URL": full_url,
                    "Remote Testing": remote_supported,
                    "Adaptive/IRT": adaptive_supported,
                    "Test Type": test_type_str,
                    "Duration": duration
                })

            # Check for next page
            next_button = await page.query_selector("li.pagination__item.-arrow.-next a")
            if next_button:
                next_url = await next_button.get_attribute("href")
                await page.goto(BASE_URL + next_url)
            else:
                break

        await browser.close()

        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Write to JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"✅ Data saved to '{OUTPUT_FILE}' with {len(results)} assessments.")

if __name__ == "__main__":
    asyncio.run(scrape_shl_catalog())