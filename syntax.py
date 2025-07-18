from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re

# 셀레니움 설정
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# 필요시 본인의 TikTok 세션 쿠키를 추가할 수도 있음.
driver = webdriver.Chrome(options=options)

# TikTok 계정 로그인 (수동 로그인 권장)
driver.get("https://www.tiktok.com/login")
print("로그인 완료 후 Enter를 눌러주세요...")
input()

# 대상 유저 페이지로 이동
username = "t4x.an"
driver.get(f"https://www.tiktok.com/@{username}/followers")

# 스크롤 함수
def scroll_followers(driver, scroll_count=30):
    for _ in range(scroll_count):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(1.5)

# 팔로워 리스트 충분히 로드
scroll_followers(driver, scroll_count=50)

# 팔로워 유저 카드 수집
follower_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "DivContainer")]')

results = []

for card in follower_cards:
    try:
        # 프로필 링크 추출
        profile_link_element = card.find_element(By.TAG_NAME, 'a')
        profile_link = profile_link_element.get_attribute('href')
        username = profile_link.split('@')[1]

        # 새 탭으로 팔로워 프로필 방문
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(profile_link)
        time.sleep(3)

        # 하트 수 (좋아요 수) 가져오기
        like_span = driver.find_element(By.XPATH, '//strong[contains(@data-e2e, "likes-count")]')
        like_count_text = like_span.text
        like_count = convert_count(like_count_text)

        # 팔로워 수 가져오기
        follower_span = driver.find_element(By.XPATH, '//strong[contains(@data-e2e, "followers-count")]')
        follower_count_text = follower_span.text
        follower_count = convert_count(follower_count_text)

        # 필터링 조건
        if like_count >= 10000 and follower_count >= 500:
            results.append({
                'username': username,
                'profile_link': profile_link,
                'likes': like_count,
                'followers': follower_count
            })

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        print("에러 발생:", e)
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        continue

# 출력
for result in results:
    print(result)

driver.quit()

# 수치 변환 함수
def convert_count(count_str):
    count_str = count_str.lower().replace(',', '')
    if 'm' in count_str:
        return int(float(count_str.replace('m','')) * 1_000_000)
    elif 'k' in count_str:
        return int(float(count_str.replace('k','')) * 1_000)
    else:
        return int(count_str)
