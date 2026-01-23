from curl_cffi.requests import AsyncSession
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from datetime import datetime
from colorama import *
import asyncio, random, string, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Humanoid:
    def __init__(self) -> None:
        self.BASE_API = "https://app.humanoidnetwork.org"
        self.HF_API = "https://huggingface.co"
        self.REF_CODE = "ONDI60" # U can change it with yours.
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.sessions = {}
        self.ua_index = 0
        self.access_tokens = {}
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Humanoid {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.txt"
        try:
            with open(filename, 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
            return None

    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address

            return address
        except Exception as e:
            return None
    
    def generate_payload(self, account: str, address: str, message: str):
        try:
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            return {
                "walletAddress": address,
                "signature": signature,
                "message": message
            }
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def generate_random_x_handle(self, min_len=5, max_len=12):
        chars = string.ascii_lowercase + string.digits
        length = random.randint(min_len, max_len)
        return ''.join(random.choice(chars) for _ in range(length))
        
    def generate_tweet_id(self, x_handle):
        if x_handle is None:
            x_handle = self.generate_random_x_handle()

        tweet_id = str(random.randint(10**17, 10**18 - 1))

        return { "tweetId": f"https://x.com/{x_handle}/status/{tweet_id}" }
    
    def get_next_user_agent(self):
        ua = self.USER_AGENTS[self.ua_index]
        self.ua_index = (self.ua_index + 1) % len(self.USER_AGENTS)
        return ua
    
    def initialize_headers(self, address: str):
        if address not in self.HEADERS:
            self.HEADERS[address] = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Origin": "https://app.humanoidnetwork.org",
                "Pragma": "no-cache",
                "Referer": "https://app.humanoidnetwork.org/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": self.get_next_user_agent()
            }
            
        return self.HEADERS[address]
    
    def get_session(self, address: str, proxy_url=None, timeout=60):
        if address not in self.sessions:
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

            session = AsyncSession(
                proxies=proxies,
                timeout=timeout, 
                impersonate="chrome120"
            )
            
            self.sessions[address] = session
        
        return self.sessions[address]
    
    async def close_session(self, address: str):
        if address in self.sessions:
            await self.sessions[address].close()
            del self.sessions[address]
    
    async def close_all_sessions(self):
        for address in list(self.sessions.keys()):
            await self.close_session(address)
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy
    
    def ensure_ok(self, response):
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}:{response.text}")
    
    async def check_connection(self, address: str, proxy_url=None):
        url = "https://api.ipify.org?format=json"
        try:
            session = self.get_session(address, proxy_url, 15)
            response = await session.get(url=url)
            self.ensure_ok(response)
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def auth_nonce(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/auth/nonce"
        payload = {"walletAddress": address}
        headers = self.initialize_headers(address)
        headers["Content-Type"] = "application/json"

        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.post(url=url, headers=headers, json=payload)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Nonce Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def auth_authenticate(self, account: str, address: str, message: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/auth/authenticate"
        payload = self.generate_payload(account, address, message)
        headers = self.initialize_headers(address)
        headers["Content-Type"] = "application/json"

        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.post(url=url, headers=headers, json=payload)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def user_data(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/user"
        headers = self.initialize_headers(address)
        headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.get(url=url, headers=headers)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to fetch user data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def apply_ref(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/referral/apply"
        payload = {"referralCode": self.REF_CODE}
        headers = self.initialize_headers(address)
        headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
        headers["Content-Type"] = "application/json"
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.post(url=url, headers=headers, json=payload)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Apply Ref Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def training_progress(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/training/progress"
        headers = self.initialize_headers(address)
        headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.get(url=url, headers=headers)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Training:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to fetch progress data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def scrape_huggingface(self, address: str, endpoint: str, proxy_url=None, retries=5):
        url = f"{self.HF_API}/{endpoint}"
        params = {"sort": "created", "withCount": True}

        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.get(url=url, params=params)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to scrape {endpoint} data from huggingface {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def submit_training(self, address: str, training_data: dict, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/training"
        headers = self.initialize_headers(address)
        headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
        headers["Content-Type"] = "application/json"
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.post(url=url, headers=headers, json=training_data)
                result = response.json()
                if response.status_code == 400:
                    err_msg = result.get("error")
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Submit Failed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} {err_msg} {Style.RESET_ALL}"
                    )
                    return None
                self.ensure_ok(response)
                return result
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Submit Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def task_lists(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/tasks"
        headers = self.initialize_headers(address)
        headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.get(url=url, headers=headers)
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to fetch tasks data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def complete_task(self, address: str, task_id: str, title: str, recurements: dict, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/tasks"
        payload = {"taskId": task_id,"data": recurements}
        headers = self.initialize_headers(address)
        headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
        headers["Content-Type"] = "application/json"
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        for attempt in range(retries):
            try:
                session = self.get_session(address, proxy_url)
                response = await session.post(url=url, headers=headers, json=payload)
                if response.status_code == 400:
                    self.log(
                        f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Already Completed {Style.RESET_ALL}"
                    )
                    return False
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Completed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(address, proxy)
            if is_valid: return True

            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
                await asyncio.sleep(1)
                continue

            return False
    
    async def process_auth_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            nonce = await self.auth_nonce(address, proxy)
            if not nonce: return False

            message = nonce.get("message")

            authenticate = await self.auth_authenticate(account, address, message, proxy)
            if not authenticate: return False
            
            self.access_tokens[address] = authenticate.get("token")

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
            )
            return True

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_auth_login(account, address, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            user = await self.user_data(address, proxy)
            if not user: return False

            refer_by = user.get("user", {}).get("referredBy", None)
            x_handle = user.get("user", {}).get("twitterId", None)
            total_points = user.get("totalPoints")

            if refer_by is None:
                await self.apply_ref(address, proxy)

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Points  :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {total_points} {Style.RESET_ALL}"
            )

            progress = await self.training_progress(address, proxy)
            if progress:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Training:{Style.RESET_ALL}")

                models_completed = progress.get("daily", {}).get("models", {}).get("completed")
                models_limit = progress.get("daily", {}).get("models", {}).get("limit")
                models_remaining = progress.get("daily", {}).get("models", {}).get("remaining")

                self.log(f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}Models{Style.RESET_ALL}"
                )
                if models_remaining > 0:
                    models = await self.scrape_huggingface(address, "models-json", proxy)
                    if models:

                        for model in models["models"]:
                            model_name = model["id"]
                            model_url = f"{self.HF_API}/{model['id']}"
                            is_private = model["private"]

                            if is_private: continue

                            training_data = {
                                "fileName": model_name,
                                "fileUrl": model_url,
                                "fileType": "model",
                                "recaptchaToken": ""
                            }

                            self.log(
                                f"{Fore.BLUE+Style.BRIGHT}   ==={Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {models_completed+1} Of {models_limit} {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}==={Style.RESET_ALL}"
                            )

                            self.log(
                                f"{Fore.BLUE+Style.BRIGHT}   Name   :{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {model_name} {Style.RESET_ALL}"
                            )
                            self.log(
                                f"{Fore.BLUE+Style.BRIGHT}   URL    :{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {model_url} {Style.RESET_ALL}"
                            )

                            submit = await self.submit_training(address, training_data, proxy)
                            if submit:
                                self.log(
                                    f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Model Submited Successfully {Style.RESET_ALL}"
                                )

                                models_completed+=1

                            if models_completed == models_limit:
                                break

                else:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Daily Limit Reached [{models_completed}/{models_limit}] {Style.RESET_ALL}"
                    )

                datasets_completed = progress.get("daily", {}).get("datasets", {}).get("completed")
                datasets_limit = progress.get("daily", {}).get("datasets", {}).get("limit")
                datasets_remaining = progress.get("daily", {}).get("datasets", {}).get("remaining")

                self.log(f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}Datasets{Style.RESET_ALL}"
                )
                if datasets_remaining > 0:
                    datasets = await self.scrape_huggingface(address, "datasets-json", proxy)
                    if datasets:

                        for dataset in datasets["datasets"]:
                            dataset_name = dataset["id"]
                            dataset_url = f"{self.HF_API}/datasets/{dataset['id']}"
                            is_private = dataset["private"]

                            if is_private: continue

                            training_data = {
                                "fileName": dataset_name,
                                "fileUrl": dataset_url,
                                "fileType": "dataset",
                                "recaptchaToken": ""
                            }

                            self.log(
                                f"{Fore.BLUE+Style.BRIGHT}   ==={Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {datasets_completed+1} Of {datasets_limit} {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}==={Style.RESET_ALL}"
                            )

                            self.log(
                                f"{Fore.BLUE+Style.BRIGHT}   Name   :{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {dataset_name} {Style.RESET_ALL}"
                            )
                            self.log(
                                f"{Fore.BLUE+Style.BRIGHT}   URL    :{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {dataset_url} {Style.RESET_ALL}"
                            )

                            submit = await self.submit_training(address, training_data, proxy)
                            if submit:
                                self.log(
                                    f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Dataset Submited Successfully {Style.RESET_ALL}"
                                )

                                datasets_completed+=1

                            if datasets_completed == datasets_limit:
                                break

                else:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Daily Limit Reached [{datasets_completed}/{datasets_limit}] {Style.RESET_ALL}"
                    )

            tasks = await self.task_lists(address, proxy)
            if tasks:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Tasks   :{Style.RESET_ALL}")

                for task in tasks:
                    task_id = task.get("id")
                    title = task.get("title")
                    type = task.get("type")
                    recurements = task.get("requirements")
                    reward = task.get("points")

                    if type == "SOCIAL_TWEET":
                        recurements = self.generate_tweet_id(x_handle)

                    complete = await self.complete_task(address, task_id, title, recurements, proxy)
                    if complete:
                        self.log(
                            f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Completed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{reward} Points{Style.RESET_ALL}"
                        )
            
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts: return

            proxy_choice, rotate_proxy = self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                use_proxy = True if proxy_choice == 1 else False
                if use_proxy: self.load_proxies()

                separator = "=" * 25
                for idx, account in enumerate(accounts, start=1):
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue
                        
                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(random.uniform(1.5, 3.0))

                await self.close_all_sessions()

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                
                delay = 24 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e
        finally:
            await self.close_all_sessions()

if __name__ == "__main__":
    try:
        bot = Humanoid()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Humanoid - BOT{Style.RESET_ALL}                                       "                              
        )