import requests
import os
from urllib.parse import urlparse
import argparse
from dotenv import load_dotenv


def shorten_link(token, url):
    bitly_url = 'https://api-ssl.bitly.com/v4/bitlinks'
    headers = {'Authorization': f'Bearer {token}'}
    body = {'long_url': url}
    response = requests.post(bitly_url, json=body, headers=headers)
    response.raise_for_status()
    return response.json()['link']


def count_clicks(bitlink, token):
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/clicks/summary'
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'units': -1,
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()['total_clicks']


def remove_link_protocol(link):
    parsed_link = urlparse(link)
    redacted_link = f'{parsed_link.netloc}{parsed_link.path}'
    return redacted_link


def is_bitlink(link, token):
    headers = {'Authorization': f'Bearer {token}'}
    link = remove_link_protocol(link)
    response = requests.get(f'https://api-ssl.bitly.com/v4/bitlinks/{link}', headers=headers)
    return response.ok


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('link', help='your link')
    return parser


def main():
    load_dotenv()
    token = os.environ['BITLY_TOKEN']
    parser = create_parser()
    namespace = parser.parse_args()
    url = namespace.link
    try:
        if is_bitlink(url, token):
            parsed_bitlink = remove_link_protocol(url)
            clicks = count_clicks(parsed_bitlink, token)
            print(f'Количество кликов: {clicks}')
        else:
            bitlink = shorten_link(token, url)
            print('bitlink:', bitlink)
    except requests.exceptions.HTTPError:
        print('Некорректная ссылка ')


if __name__ == '__main__':
    main()
