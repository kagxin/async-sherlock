import fire
import os
import json
from colorama import Fore, Style, init
import aiohttp
import asyncio


def print_info(title, info):
    print(Style.BRIGHT + Fore.GREEN + "[" +
          Fore.YELLOW + "*" +
          Fore.GREEN + f"] {title}" +
          Fore.WHITE + f" {info}" +
          Fore.GREEN + " on:")


def print_error(err, errstr, var, verbose=False):
    print(Style.BRIGHT + Fore.WHITE + "[" +
          Fore.RED + "-" +
          Fore.WHITE + "]" +
          Fore.RED + f" {errstr}" +
          Fore.YELLOW + f" {err if verbose else var}")


def format_response_time(response_time=-1, verbose=False):
    return " [{} ms]".format(response_time) if verbose else ""


def print_found(social_network, url, response_time=-1, verbose=False):
    print((Style.BRIGHT + Fore.WHITE + "[" +
           Fore.GREEN + "+" +
           Fore.WHITE + "]" +
           format_response_time(response_time, verbose) +
           Fore.GREEN + f" {social_network}:"), url)


def print_not_found(social_network, response_time=-1, verbose=False):
    print((Style.BRIGHT + Fore.WHITE + "[" +
           Fore.RED + "-" +
           Fore.WHITE + "]" +
           format_response_time(response_time, verbose) +
           Fore.GREEN + f" {social_network}:" +
           Fore.YELLOW + " Not Found!"))


def print_invalid(social_network, msg):
    print((Style.BRIGHT + Fore.WHITE + "[" +
           Fore.RED + "-" +
           Fore.WHITE + "]" +
           Fore.GREEN + f" {social_network}:" +
           Fore.YELLOW + f" {msg}"))


def sherlock(username, site_data_file='data.json'):
    init(autoreset=True)
    username = username
    data_file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), site_data_file)
    site_data = json.load(open(data_file_path))

    async def fetch(social_network, net_info):
        async with aiohttp.ClientSession() as session:
            error_type = net_info['errorType']
            url = net_info['url'].format(username)
            try:
                response = await session.get(url, verify_ssl=False)
            except Exception as e:
                print_error(e, "HTTP Error:", url)
                return

            status_code = response.status
            try:
                text = await response.text()
            except UnicodeDecodeError as e:
                print_error(e, "UnicodeDecodeError:", url)
                return

            if error_type == "message":
                error = net_info.get("errorMsg")
                if not error in text:
                    print_found(social_network, url)
                else:
                    print_not_found(social_network)

            elif error_type == "status_code":
                if not status_code >= 300 or status_code < 200:
                    print_found(social_network, url)
                else:
                    print_not_found(social_network)

            elif error_type == "response_url":

                if 200 <= status_code < 300:
                    print_found(social_network, url)
                else:
                    print_not_found(social_network)
            elif error_type == "":
                print_invalid(social_network, "Error!")

    loop = asyncio.get_event_loop()
    gather = asyncio.gather(
        *[fetch(social_network, net_info) for social_network, net_info in site_data.items()]
    )
    loop.run_until_complete(gather)


def command(username):
    sherlock(username, 'data.json')


if __name__ == '__main__':
    fire.Fire(command)
