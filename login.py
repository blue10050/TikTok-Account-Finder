import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def parse_count(text):
    text = text.strip().upper()
    try:
        if text.endswith('M'):
            return int(float(text[:-1]) * 1_000_000)
        elif text.endswith('K'):
            return int(float(text[:-1]) * 1_000)
        else:
            return int(text.replace(',', ''))
    except:
        return 0

def scroll_followers_container(driver, container, max_scrolls=200, delay=2):
    last_height = 0
    scroll_attempt = 0

    for _ in range(max_scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(delay)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)

        if new_height == last_height:
            scroll_attempt += 1
            if scroll_attempt >= 3:
                print("더 이상 스크롤할 내용이 없습니다.")
                break
        else:
            scroll_attempt = 0
            last_height = new_height

options = uc.ChromeOptions()
options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

driver = uc.Chrome(options=options)

try:
    driver.get("https://www.tiktok.com/login")
    print("로그인 해주세요. 완료 후 Enter 키를 눌러주세요.")
    input()

    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[data-e2e='user-avatar']")))
    except:
        print("프로필 아이콘 로드 대기 실패, 다음 단계로 진행")

    driver.get("https://www.tiktok.com/@t4x.an")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-e2e='followers']")))

    follower_tab = driver.find_element(By.CSS_SELECTOR, "span[data-e2e='followers']")
    follower_tab.click()
    time.sleep(3)

    scroll_container = driver.find_element(By.CSS_SELECTOR, "div.css-wq5jjc-DivUserListContainer.eorzdsw0")
    scroll_followers_container(driver, scroll_container, max_scrolls=200, delay=2)

    user_links = set()
    follower_items = scroll_container.find_elements(By.CSS_SELECTOR, "div.css-1q2pvy0-DivUserItem.es616eb1")
    for item in follower_items:
        try:
            user_link_elem = item.find_element(By.CSS_SELECTOR, "a.css-7fu252-StyledUserInfoLink.es616eb3")
            user_links.add(user_link_elem.get_attribute("href"))
        except StaleElementReferenceException:
            continue

    filtered_users = []

    for i, user_url in enumerate(user_links):
        try:
            driver.get(user_url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "strong[data-e2e='followers-count']")))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "strong[data-e2e='likes-count']")))

            follower_text = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='followers-count']").text
            likes_text = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='likes-count']").text

            follower_count = parse_count(follower_text)
            likes_count = parse_count(likes_text)

            username = user_url.split("@")[-1]

            if likes_count >= 10_000 and follower_count >= 500:
                filtered_users.append({
                    "username": username,
                    "followers": follower_count,
                    "likes": likes_count,
                })

            print(f"[{i+1}] {username}: {follower_count} followers / {likes_count} likes")

        except Exception as e:
            print(f"Error processing user #{i+1} at {user_url}: {e}")
            continue

    print("조건에 맞는 사용자 목록:")
    for u in filtered_users:
        print(u)

finally:
    time.sleep(5)
    driver.quit()
