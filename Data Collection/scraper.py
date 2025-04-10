import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- URL Setup ----------
base_url = "https://www.myntra.com"

men_categories = [
    "men-sweatshirts", "men-sweaters", "men-jackets", "men-blazers", "rain-jacket",
    "men-suits", "men-kurtas", "sherwani", "nehru-jackets", "dhoti",
    "men-jeans", "men-casual-trousers", "men-formal-trousers", "mens-shorts", "men-trackpants"
]

kids_categories = [
    "https://www.myntra.com/kids?f=Categories%3ATshirts%3A%3AGender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kids?f=Categories%3AShirts%3A%3AGender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kids?f=Categories%3AShorts%3A%3AGender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kids?f=Categories%3AJeans%3A%3AGender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kids?f=Categories%3ATrousers%3A%3AGender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kids?f=Categories%3AClothing%20Set%3A%3AGender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/ki-etnhc?f=Gender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kdsprtywr?f=Gender%3Aboys%2Cboys%20girls",
    "https://www.myntra.com/kids?f=Categories%3ADresses%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids?f=Categories%3ATops%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids?f=Categories%3ATshirts%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids?f=Categories%3AClothing%20Set%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids?f=Categories%3ALehenga%20Choli",
    "https://www.myntra.com/kids?f=Categories%3AKurta%20Sets%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kdsprtywr?f=Gender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids?f=Categories%3ADungarees%2CJumpsuit%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids?f=Categories%3AShorts%2CSkirts%3A%3AGender%3Aboys%20girls%2Cgirls",
    "https://www.myntra.com/kids-nightwear?f=Gender%3Aboys%20girls%2Cgirls"
]

women_categories = [
    "women-kurtas-kurtis-suits", "ethnic-tops", "saree", "women-ethnic-wear",
    "women-ethnic-bottomwear?f=categories%3AChuridar%2CLeggings%2CSalwar", "skirts-palazzos", 
    "dress-material", "lehenga-choli", "dupatta-shawl", "women-jackets",
    "dresses?f=Gender%3Amen%20women%2Cwomen", "tops",
    "myntra-fashion-store?f=Categories%3ATshirts%3A%3AGender%3Amen%20women%2Cwomen",
    "women-jeans", "women-trousers", "women-shorts-skirts",
    "myntra-fashion-store?f=Categories%3AClothing%20Set%2CCo-Ords%3A%3AGender%3Amen%20women%2Cwomen",
    "playsuit?f=Gender%3Amen%20women%2Cwomen", "jumpsuits?f=Gender%3Amen%20women%2Cwomen",
    "women-shrugs", "women-sweaters-sweatshirts", "women-jackets-coats", "women-blazers-waistcoats"
]

sorts = ["", "?sort=recommended", "?sort=new", "?sort=popularity"]

def generate_all_urls():
    urls = []

    # Men and Women category URLs
    for category in men_categories + women_categories:
        for sort in sorts:
            base = f"{base_url}/{category}"
            if sort:
                sep = "&" if "?" in base else "?"
                base += f"{sep}{sort[1:]}"
            urls.append(base)

    # Kids are full URLs; append sort variants
    for kid_url in kids_categories:
        urls.append(kid_url)
        urls.append(f"{kid_url}&sort=recommended")
        urls.append(f"{kid_url}&sort=new")

    return urls

all_urls = generate_all_urls()

# ---------- CSV Setup ----------
csv_file = open("Myntra.csv", mode="a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
id_counter = 1
if csv_file.tell() == 0:
    csv_writer.writerow(["ID", "Manufacturer Details"])

# ---------- WebDriver Setup ----------
def start_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    return driver, wait

# ---------- Product Extraction ----------
def extract_product_details(driver, wait, product_index):
    global id_counter
    try:
        product_image = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"(//img[@class='img-responsive'])[{product_index}]"))
        )
        product_image.click()
        driver.switch_to.window(driver.window_handles[1])
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # ---------- Try size selection ----------
        try:
            size_buttons = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.size-buttons-buttonContainer button"))
            )

            size_found = False
            preferred_sizes = ['L', 'M', 'XL', 'S', 'XS', 'XXL', '34', '32', '36', '30', '38', 'OneSize']

            for button in size_buttons:
                try:
                    size_text = button.text.strip()
                    if size_text in preferred_sizes or 'Y' in size_text:
                        driver.execute_script("arguments[0].click();", button)
                        size_found = True
                        break
                except:
                    continue

            if not size_found:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return

        except:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return

        # ---------- Supplier info button ----------
        supplier_info_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Supplier Information')]")
        if not supplier_info_elements:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return

        driver.execute_script("arguments[0].scrollIntoView();", supplier_info_elements[0])
        driver.execute_script("arguments[0].click();", supplier_info_elements[0])

        # ---------- Modal for manufacturer details ----------
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'Modal-modalContent')]"))
        )
        try:
            header = modal.find_element(By.XPATH, ".//h4[contains(text(), 'Manufacturer Details')]")
            detail = header.find_element(By.XPATH, ".//following-sibling::p").text.strip()
            if detail:
                csv_writer.writerow([id_counter, detail])
                id_counter += 1
        except:
            pass

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception:
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass


# ---------- Main Scraping Loop ----------
for url in all_urls:
    try:
        try:
            driver.quit()
        except:
            pass
        driver, wait = start_driver()

        driver.get(url)
        time.sleep(3)
        for _ in range(2):
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Only first 50 products
        for i in range(1, 51):
            start_time = time.time()
            try:
                extract_product_details(driver, wait, i)
            except Exception:
                continue
            if time.time() - start_time > 60:
                print(f"Timed out on product {i}, skipping.")
                continue

    except Exception as e:
        print(f"Error loading page: {url}")
        print(e)
        continue

# ---------- Cleanup ----------
csv_file.close()
driver.quit()
