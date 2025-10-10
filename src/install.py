!pip install google-generativeai
!pip install selenium
!pip install webdriver-manager
!apt-get update
!apt install chromium-chromedriver

##第二個區塊
# 2. 手動安裝與最新 WebDriver 相符的 Chrome 瀏覽器
#    這能確保版本匹配，避免啟動錯誤
!wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/114.0.5735.90/linux64/chrome-linux64.zip
!unzip -q chrome-linux64.zip -d /bin/
