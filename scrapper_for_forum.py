from time import sleep
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import html2text
import os


def get_html(url, attempts=1, timeout=10, delay=0):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for i in range(attempts):
        try:
            response = urlopen(url, timeout=timeout, context=ctx)

            # check OK code from web server
            if response.code != 200:
                sleep(delay)
                continue

            html_bytes = response.read()
            html_text = html_bytes.decode("utf8")
            html_tree = BeautifulSoup(html_text, 'html.parser')

            html_converter = html2text.HTML2Text()
            html_converter.ignore_links = True
            html_converter.ignore_images = True

            title = html_tree.find("title")
            article_text = title.get_text(strip=True)
            posts = html_tree.find_all("div", {"class": "post"})  #класс отвечающий за само сообщение на форуме
            date = html_tree.find_all(
                lambda tag: tag.name == 'div' and tag.get('class') == ['smalltext'])  #дата, время, номер поста
            posters = html_tree.find_all("div", {
                "class": "poster col-md-2"})  #класс в котором вложен тег h4 - в котором содержется имя автора поста
            if len(posts) != len(posters):
                raise Exception("Ошибка Формата. Посты не соответствуют авторам.")
            else:
                print("len(posts) == len(posters")
            page_text = ''

            for i in range(len(posts)):
                name_text = posters[i].h4.get_text(strip=True)
                date_text = date[i].get_text(strip=True)
                message_html = str(posts[i])
                message_text = html_converter.handle(message_html)

                page_text += '* * *  ' + name_text + '  * * *'
                page_text += '\n--------------------------------------\n'
                page_text += date_text
                page_text += '\n--------------------------------------\n'
                page_text += message_text + '\n'

                print(page_text)
            return page_text, html_text, article_text, i

        except Exception as e:
            print(e)
            sleep(delay)

    return None


def get_pages(url_template, first_page_id=0, last_page_id=120, step=15, delay=2):
    missed_urls = []
    pages = []
    current_page_num = 0

    for id in range(first_page_id, last_page_id + 1, step):
        url = url_template.format(id)
        result = get_html(url)

        if result is None:
            missed_urls.append(url)
            print(url + '    Missed!')
        else:
            page_text, html_text, article_text, i = result
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_name = f"{article_text}.txt"
            file_path = os.path.join(current_dir, file_name)
            pages.append(result)
            current_page_num += 1
            with open(file_path, "a", encoding="utf-8") as f:  # with open(file_path, "w", encoding="utf-8") as file:
                if id < 1:
                    f.write("+++|||" + article_text + "|||+++" + "\n" + "стр." + str(
                        current_page_num) + ":" + "\n--------------------------------------\n" + page_text + "\n\n")
                    print(url + '    OK!')

                else:
                    f.write(str(current_page_num) + ":" + page_text + "\n\n")
                    print(url + '    OK!')

            sleep(delay)

    if missed_urls:  # the same as if len(missing_urls) != 0:
        print('Missed Urls:')
        for url in missed_urls:
            print(url)
    else:
        print('No missed urls')

    return pages


url_template = 'https://example_page.com/forum/index.php/topic,8427.{}.html'

pages = get_pages(url_template, first_page_id=0, last_page_id=200, step=1)
