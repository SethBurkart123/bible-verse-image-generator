from rich.logging import RichHandler
from rich.progress import Progress
from rich.console import Console
from dotenv import load_dotenv
import requests
import logging
import os

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])
log = logging.getLogger("pexels_downloader")

# Load environment variables
load_dotenv()

# Pexels API configuration
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"

console = Console()

def download_image(url: str, filepath: str) -> None:
    response = requests.get(url, headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': 'Bearer 429149923_G_tLXy8ypVFThKceT43RUw',
            'content-type': 'application/json',
            'cookie': '_cfuvid=urqgYlcW8RFToETijuS5OOG1KfJXuoV9IsFuQkubX6Y-1726981804758-0.0.1.1-604800000; active_experiment={"id":"getty_big_ad","variant":{"id":"fixed_height_grid_with_ad"}}; _sp_ses.9ec1=*; ab.storage.deviceId.5791d6db-4410-4ace-8814-12c903a548ba=%7B%22g%22%3A%22cafff100-d05e-2b24-2408-587dd2d6204d%22%2C%22c%22%3A1717750013170%2C%22l%22%3A1726982437036%7D; locale=en-US; NEXT_LOCALE=en-US; __cf_bm=A53zu5ExO5XZ1zZakrPtz1f0sq1UJgqYpMtTrAlrorA-1726982946-1.0.1.1-H61U5aBneDeHgHCa76Q7CIMDAi67gjKD3riOlAQk7eeOVX3pCTYEp13sSh3vxugBjh7jyBerigtBOljwiyAPOQ; google-one-tap-skip-prompt=true; g_state={"i_l":0}; pexels_auth=true; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6IlcxczBNamt4TkRrNU1qTmRMQ0lrTW1Fa01UQWtlVGRQV2twc1RsbHpkME55TkZseEx6UkZSRzUyWlNJc0lqRTNNalk1T0RJNU5UY3VOVGs1TkRnMElsMD0iLCJleHAiOiIyMDI1LTA5LTIyVDA1OjI5OjE3LjU5OVoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--257428be407f14eb4a427c9fc9d5600454a6531a; authHeader=Bearer 429149923_G_tLXy8ypVFThKceT43RUw; ab.storage.sessionId.5791d6db-4410-4ace-8814-12c903a548ba=%7B%22g%22%3A%22a6f0d8ef-8c49-9cfd-9f15-956be2611fe2%22%2C%22e%22%3A1726984834338%2C%22c%22%3A1726982437036%2C%22l%22%3A1726983034338%7D; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Sep+22+2024+15%3A42%3A57+GMT%2B1000+(Australian+Eastern+Standard+Time)&version=202301.1.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0&AwaitingReconsent=false; cf_clearance=o_N.oFWks6CT2mugrjegWKT4gGOAAYljewJRvI0wp_k-1726983777-1.2.1.1-1y7YBKv9EtRSm_UF6frb8O2mjddKT_FUapQPvaEWsrcoUB1CDMnCEJfv0yJwAmosa0ZQv71bz6uIyvDJOmxNTNkvP6KsRWf1OSZ.s99ETMkQ8D3.Fq0QQU7JzHhpnpa7bj92SyVOyaZpMTJ_VclhKUS_7t0cOrni.1tsXMyUKwN3Ub_85N9l2D7kBpWhIUBXDvX0QN5qqyGUvcE2Xhp23m4JnsZ76h9fr7Pzeph6sVoN11FTQmc8OlSYjcxDuDv7zkPJsf24aUP9pOkUio.oR4i2.3jVaoJshxSmOCMyGRZWMYKgnxZafE6cnB1vz6jVI8l23Hq_AlnXri78s7BgaWXUSIMDJ9Mcac_IWnKbRMzhwyUYOsK5c6xjtcIAUXKpPmiHleRNG6.ODdSo5Fi1PQ; country-code-v2=AU; _sp_id.9ec1=d5ec39f7-a9b6-4e92-946c-cf902d2b1597.1717750128.4.1726983841.1725658644.f9828085-95c3-49cf-a4d0-1a6ebf6f0bfa.3eef8bad-6446-4263-9e54-6f2492a21744.3cf50fad-b2ce-49a7-973e-08734f0ac6a9.1726981805312.27; _pexels_session=i6K6IvnTYCAhkSt4dS3XnWp%2B%2FEXPC9%2Bsqxh7uCoagL0gPVzYh5cT3QfDsxSBm9SSoq0%2Fj%2FDpQHYBdBIxew3Z3EP7Fu%2FCC0rKssYV%2BVelbyKQ9QEzYBaCOY%2FFEvP03Fr9ROwFECJ5xa4Y%2BidftneHRVrd%2BcWF7XjoeGiyn0S%2BTYiTCnkegiq42rzovOkn5Bza1FGO%2FdWNqHi88k58ItGZtKf65bIIAzDxJ5lgteYp0N5Aea40a4KrnXBgllgS6KYBt98NBkEgHlpO4R4tdNTu8uzVdpoc3R%2Fy3sNrjT1KBiva3dMkj9CxbbCBRCk2KQPIX3l7VAet1S%2FripdRlBRiJXH218jxS50qp%2FMXynMuQ2jUazYo8Xf2sP%2FKLKNOut%2F9nDXB1Z3XLIAClWhAg2MHzzE6bpuDfdSvxbYuEM1rmKLrnjhhKcFdhqFSupv7gp0MFuDoupNA4QnEPTz7gA9Pl%2FSYSPvQWowp3pnqFgIcpN5yKYXtqz8mqKPcEDuasQtHAW%2FMi9FZNnzUu%2BE47YoiG3dYGdu55um%2FyfT66TbK6g%3D%3D--oZl0d6HQ2Mr8MjAt--cHg75RYkkXRW3ChylIdpBw%3D%3D',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://www.pexels.com/search/nature/',
            'sec-ch-ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'secret-key': 'H2jk9uKnhRmL6WPwh89zBezWvr',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-client-type': 'react',
            'x-forwarded-cf-connecting-ip': '',
            'x-forwarded-cf-ipregioncode': '',
            'x-forwarded-http_cf_ipcountry': ''
        })
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        log.info(f"Downloaded: {filepath}")
    else:
        log.error(f"Failed to download: {url}")

def search_images(query: str, num_images: int) -> list:
    all_photos = []
    page = 1

    while len(all_photos) < num_images:
        url = f'https://www.pexels.com/en-us/api/v3/search/photos'
        params = {
            'query': query,
            'page': page,
            'per_page': min(24, num_images),
            'orientation': 'portrait',
            'size': 'all',
            'color': 'all',
            'sort': 'popular',
            'seo_tags': 'true'
        }
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': 'Bearer 429149923_G_tLXy8ypVFThKceT43RUw',
            'content-type': 'application/json',
            'cookie': '_cfuvid=urqgYlcW8RFToETijuS5OOG1KfJXuoV9IsFuQkubX6Y-1726981804758-0.0.1.1-604800000; active_experiment={"id":"getty_big_ad","variant":{"id":"fixed_height_grid_with_ad"}}; _sp_ses.9ec1=*; ab.storage.deviceId.5791d6db-4410-4ace-8814-12c903a548ba=%7B%22g%22%3A%22cafff100-d05e-2b24-2408-587dd2d6204d%22%2C%22c%22%3A1717750013170%2C%22l%22%3A1726982437036%7D; locale=en-US; NEXT_LOCALE=en-US; __cf_bm=A53zu5ExO5XZ1zZakrPtz1f0sq1UJgqYpMtTrAlrorA-1726982946-1.0.1.1-H61U5aBneDeHgHCa76Q7CIMDAi67gjKD3riOlAQk7eeOVX3pCTYEp13sSh3vxugBjh7jyBerigtBOljwiyAPOQ; google-one-tap-skip-prompt=true; g_state={"i_l":0}; pexels_auth=true; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6IlcxczBNamt4TkRrNU1qTmRMQ0lrTW1Fa01UQWtlVGRQV2twc1RsbHpkME55TkZseEx6UkZSRzUyWlNJc0lqRTNNalk1T0RJNU5UY3VOVGs1TkRnMElsMD0iLCJleHAiOiIyMDI1LTA5LTIyVDA1OjI5OjE3LjU5OVoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--257428be407f14eb4a427c9fc9d5600454a6531a; authHeader=Bearer 429149923_G_tLXy8ypVFThKceT43RUw; ab.storage.sessionId.5791d6db-4410-4ace-8814-12c903a548ba=%7B%22g%22%3A%22a6f0d8ef-8c49-9cfd-9f15-956be2611fe2%22%2C%22e%22%3A1726984834338%2C%22c%22%3A1726982437036%2C%22l%22%3A1726983034338%7D; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Sep+22+2024+15%3A42%3A57+GMT%2B1000+(Australian+Eastern+Standard+Time)&version=202301.1.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0&AwaitingReconsent=false; cf_clearance=o_N.oFWks6CT2mugrjegWKT4gGOAAYljewJRvI0wp_k-1726983777-1.2.1.1-1y7YBKv9EtRSm_UF6frb8O2mjddKT_FUapQPvaEWsrcoUB1CDMnCEJfv0yJwAmosa0ZQv71bz6uIyvDJOmxNTNkvP6KsRWf1OSZ.s99ETMkQ8D3.Fq0QQU7JzHhpnpa7bj92SyVOyaZpMTJ_VclhKUS_7t0cOrni.1tsXMyUKwN3Ub_85N9l2D7kBpWhIUBXDvX0QN5qqyGUvcE2Xhp23m4JnsZ76h9fr7Pzeph6sVoN11FTQmc8OlSYjcxDuDv7zkPJsf24aUP9pOkUio.oR4i2.3jVaoJshxSmOCMyGRZWMYKgnxZafE6cnB1vz6jVI8l23Hq_AlnXri78s7BgaWXUSIMDJ9Mcac_IWnKbRMzhwyUYOsK5c6xjtcIAUXKpPmiHleRNG6.ODdSo5Fi1PQ; country-code-v2=AU; _sp_id.9ec1=d5ec39f7-a9b6-4e92-946c-cf902d2b1597.1717750128.4.1726983841.1725658644.f9828085-95c3-49cf-a4d0-1a6ebf6f0bfa.3eef8bad-6446-4263-9e54-6f2492a21744.3cf50fad-b2ce-49a7-973e-08734f0ac6a9.1726981805312.27; _pexels_session=i6K6IvnTYCAhkSt4dS3XnWp%2B%2FEXPC9%2Bsqxh7uCoagL0gPVzYh5cT3QfDsxSBm9SSoq0%2Fj%2FDpQHYBdBIxew3Z3EP7Fu%2FCC0rKssYV%2BVelbyKQ9QEzYBaCOY%2FFEvP03Fr9ROwFECJ5xa4Y%2BidftneHRVrd%2BcWF7XjoeGiyn0S%2BTYiTCnkegiq42rzovOkn5Bza1FGO%2FdWNqHi88k58ItGZtKf65bIIAzDxJ5lgteYp0N5Aea40a4KrnXBgllgS6KYBt98NBkEgHlpO4R4tdNTu8uzVdpoc3R%2Fy3sNrjT1KBiva3dMkj9CxbbCBRCk2KQPIX3l7VAet1S%2FripdRlBRiJXH218jxS50qp%2FMXynMuQ2jUazYo8Xf2sP%2FKLKNOut%2F9nDXB1Z3XLIAClWhAg2MHzzE6bpuDfdSvxbYuEM1rmKLrnjhhKcFdhqFSupv7gp0MFuDoupNA4QnEPTz7gA9Pl%2FSYSPvQWowp3pnqFgIcpN5yKYXtqz8mqKPcEDuasQtHAW%2FMi9FZNnzUu%2BE47YoiG3dYGdu55um%2FyfT66TbK6g%3D%3D--oZl0d6HQ2Mr8MjAt--cHg75RYkkXRW3ChylIdpBw%3D%3D',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://www.pexels.com/search/nature/',
            'sec-ch-ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'secret-key': 'H2jk9uKnhRmL6WPwh89zBezWvr',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-client-type': 'react',
            'x-forwarded-cf-connecting-ip': '',
            'x-forwarded-cf-ipregioncode': '',
            'x-forwarded-http_cf_ipcountry': ''
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            log.error(f"Failed to fetch images: {response.status_code}")
            break

        data = response.json()
        photos = data.get("data", [])
        all_photos.extend(photos)

        if not photos or len(all_photos) >= num_images:
            break

        page += 1

    return all_photos[:num_images]

def download_images(query: str, num_images: int) -> None:
    images = search_images(query, num_images)
    console.print(images)
    downloaded_images = set()

    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading images...", total=len(images))

        for image in images:
            image_url = image["attributes"]["image"]["large"]  # At least 1080px wide
            image_id = image["id"]

            if image_url not in downloaded_images:
                filepath = os.path.join("backgrounds", f"{image_id}.jpg")
                download_image(image_url, filepath)
                downloaded_images.add(image_url)
                progress.update(task, advance=1)
            else:
                log.warning(f"Skipping duplicate image: {image_id}")

    log.info(f"Downloaded {len(downloaded_images)} unique images")

if __name__ == "__main__":
    if not os.path.exists("backgrounds"):
        os.makedirs("backgrounds")

    default_search_query = "nature"
    default_num_images = 10

    search_query = console.input(f"Enter search query [default: {default_search_query}]: ").strip() or default_search_query
    
    while True:
        num_images_input = console.input(f"Enter number of images to download [default: {default_num_images}]: ").strip() or str(default_num_images)
        try:
            num_images_to_download = int(num_images_input)
            if num_images_to_download > 0:
                break
            else:
                console.print("[bold red]Please enter a positive number.[/bold red]")
        except ValueError:
            console.print("[bold red]Please enter a valid number.[/bold red]")

    console.print(f"[bold green]Downloading {num_images_to_download} images for query: {search_query}[/bold green]")
    download_images(search_query, num_images_to_download)