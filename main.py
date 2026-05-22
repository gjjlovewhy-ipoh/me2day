import requests
from bs4 import BeautifulSoup
import re
import time

# ===================== 三个站点分页配置 =====================
# 1. 歌宝古风 1-11页
SITE1_NAME = "歌宝古风网"
SITE1_URL = "https://www.gequbao.net/s/%E6%8A%96%E9%9F%B3%E5%8F%A4%E9%A3%8E?page={}"
SITE1_PAGE = range(1, 12)

# 2. corper.cn 1-5页
SITE2_NAME = "corper音乐站"
SITE2_URL = "https://corper.cn/index.php?page={}&kw=.mp3"
SITE2_PAGE = range(1, 6)

# 3. mpimg.cn 调整为 1-41页
SITE3_NAME = "mpimg音乐站"
SITE3_URL = "https://mpimg.cn/index.php?page={}&kw=.mp3"
SITE3_PAGE = range(1, 42)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.baidu.com"
}
OUT_FILE = "三合一歌曲资源汇总.txt"

# 通用嗅探真实MP3链接
def get_real_mp3(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = "utf-8"
        match = re.search(r'https?://[^\s"<>]+\.mp3', r.text)
        return match.group() if match else "未获取到资源"
    except Exception:
        return "获取失败"

# 抓取歌宝古风
def crawl_site1():
    data = []
    for p in SITE1_PAGE:
        try:
            r = requests.get(SITE1_URL.format(p), headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href^='/song/']"):
                title = a.get_text(strip=True)
                detail = "https://www.gequbao.net" + a["href"]
                mp3 = get_real_mp3(detail)
                data.append([SITE1_NAME, title, detail, mp3])
                time.sleep(0.6)
            print(f"✅ 歌宝第{p}页完成")
        except Exception as e:
            print(f"❌ 歌宝第{p}页异常：{e}")
        time.sleep(0.8)
    return data

# 抓取corper
def crawl_site2():
    data = []
    for p in SITE2_PAGE:
        try:
            r = requests.get(SITE2_URL.format(p), headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("table a"):
                href = a["href"]
                if "down" in href or "file" in href:
                    title = a.get_text(strip=True)
                    link = href if href.startswith("http") else f"https://corper.cn/{href.lstrip('/')}"
                    mp3 = get_real_mp3(link)
                    data.append([SITE2_NAME, title, link, mp3])
            print(f"✅ corper第{p}页完成")
        except Exception as e:
            print(f"❌ corper第{p}页异常：{e}")
        time.sleep(0.8)
    return data

# 抓取mpimg 1-41页
def crawl_site3():
    data = []
    for p in SITE3_PAGE:
        try:
            r = requests.get(SITE3_URL.format(p), headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("table a"):
                href = a["href"]
                if "down" in href or "file" in href:
                    title = a.get_text(strip=True)
                    link = href if href.startswith("http") else f"https://mpimg.cn/{href.lstrip('/')}"
                    mp3 = get_real_mp3(link)
                    data.append([SITE3_NAME, title, link, mp3])
            print(f"✅ mpimg第{p}页完成")
        except Exception as e:
            print(f"❌ mpimg第{p}页异常：{e}")
        time.sleep(0.8)
    return data

if __name__ == "__main__":
    print("=== 三合一定时爬虫开始执行 ===")
    all_data = []
    all_data.extend(crawl_site1())
    all_data.extend(crawl_site2())
    all_data.extend(crawl_site3())

    # 写入汇总文件
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== 三合一歌曲抓取结果 执行时间：{time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"本次合计抓取：{len(all_data)} 首歌曲\n\n")
        for idx, (site, name, detail, mp3) in enumerate(all_data, 1):
            f.write(f"{idx}. 来源站点：{site}\n")
            f.write(f"   歌曲名称：{name}\n")
            f.write(f"   详情地址：{detail}\n")
            f.write(f"   真实MP3链接：{mp3}\n\n")

    print(f"\n🎉 本轮抓取结束，共获取 {len(all_data)} 条资源")
    print(f"📄 结果已保存至 {OUT_FILE}")
