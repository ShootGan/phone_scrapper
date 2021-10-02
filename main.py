import sys
import requests
import bs4
import re
from collections import Counter
import validators


def get_soup(url: str) -> bs4.BeautifulSoup:
    """get url soup"""
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    return soup


def search_numbers_by_href(page_soup: bs4.BeautifulSoup) -> list:
    """search number by a tags"""
    phone_numbers = []
    main_page_numbers = page_soup.select("a[href^=tel]")
    for phone_number in main_page_numbers:
        if not re.search('[a-zA-Z]', phone_number.text) and re.search(r'(\+?\d{2})?(\d{3} ?)?( ?\d{2,3}){3,4}',
                                                                      phone_number.text):
            checked_phone_number = re.search(r'(\+?\d{2})?(\d{3} ?)?( ?\d{2,3}){3,4}', phone_number.text)
            phone_numbers.append(checked_phone_number.group(0))
    return phone_numbers


def get_sub_pages(soup: bs4.BeautifulSoup, url: str) -> list:
    """extract sub pages links"""
    pages_urls = []
    sub_pages_regex = ['kontakt', 'contact', 'about', 'o-nas']

    try:
        for search in sub_pages_regex:
            sub_page = soup.find('a', text=re.compile(search, re.IGNORECASE))['href']
            if validators.url(sub_page) and sub_page not in pages_urls:
                pages_urls.append(sub_page)
            elif not re.search(r'@| |\+', sub_page) and sub_page.startswith('/') or sub_page.startswith('./'):
                if sub_page.startswith('./'):
                    sub_page = sub_page[1:]
                pages_urls.append(url + sub_page)

        pages_urls = list(dict.fromkeys(pages_urls))
        return pages_urls
    except:
        return [f'{url}/{page}' for page in sub_pages_regex]


def search_number_by_regex(pages_soup_list: list) -> str:
    """search number on page content"""
    for sub_page_soup in pages_soup_list:

        phone_number = re.search(r'(\+?\d{2})?( ?\d{2,3} \d{2,3} \d{2,3})( \d{2,3})?', sub_page_soup.get_text())

        if phone_number:
            phone_number = (phone_number.group(0))
            check_phone_number = sum(char.isdigit() for char in phone_number)
            if 9 <= check_phone_number < 13:
                return phone_number


def get_phone_number(url: str) -> str:
    """main function"""

    # get main page
    try:
        soup = get_soup(url)
    except Exception as e:
        return f'Bad url \n  {str(e)}'
    # try find number on main mage by a tag
    phone_numbers = search_numbers_by_href(soup)
    if phone_numbers:
        return Counter(phone_numbers).most_common(1)[0][0]
    # try find on sub pages
    pages_soup_list = []
    sub_pages_url_list = get_sub_pages(soup, url)

    for sub_page_url in sub_pages_url_list:
        try:
            pages_soup_list.append(get_soup(sub_page_url))
        except Exception as e:
            print(str(e))
            continue

    for sub_page_soup in pages_soup_list:
        phone_numbers = search_numbers_by_href(sub_page_soup)
        if phone_numbers:
            return Counter(phone_numbers).most_common(1)[0][0]
    # try find by scanning all text
    pages_soup_list.insert(0, soup)
    phone_number = search_number_by_regex(pages_soup_list)
    return phone_number if phone_number else f'{url} number not found '


if __name__ == '__main__':
    print(get_phone_number(sys.argv[1]))
