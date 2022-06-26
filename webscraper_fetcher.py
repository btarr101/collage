import io
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from PIL import Image
from defopt import run
from urllib.parse import urlparse


def download_image(url: str, output: Path) -> None:
    """
    Downloads an image from an url.

    :param url: the address to download the image from online.
    :param output: the local path where to download the image to.
    """

    try:
        content = requests.get(url).content
        file = io.BytesIO(content)
        image = Image.open(file)
        rgb_image = Image.new("RGB", image.size, (255, 255, 255))
        rgb_image.paste(image)
        image.close()
        rgb_image.save(output, "JPEG")

    except Exception as e:
        print(f"\t-> Error: {e}, image not downloaded")


class WebscraperFetcher:
    """
    Class that fetches images from scraping a webpage.
    """

    def __init__(self, url: str, count: int):
        """
        Constructs a new instance that fetches from a webpage.

        :param url: the webpage to scrape from.
        :param count: the amount of images to scrape.
        """
        self.url = url
        self.count = count

    def fetch_to_dir(self, local_image_dir: Path) -> None:
        """
        Fetches images from a web scrape to a local directory.

        :param local_image_dir: the local directory to fetch to.
        """

        page = requests.get(self.url)
        doc = BeautifulSoup(page.text, "html.parser")

        tags = doc.find_all("img")[:self.count]
        for i, tag in enumerate(tags):
            source = tag['src']
            filename = Path(urlparse(source).path).name + str(i)
            download_image(source, local_image_dir / filename)
            print(f"Downloaded {source}")


def main(*, count: int, local_dir: Path) -> None:
    """
    Scrapes for images and downloads them.

    :param count: the number of images to scrape.
    :param local_dir: the local directory to download to.
    """

    if not local_dir.exists():
        local_dir.mkdir(parents=True)

    url = 'https://www.google.com/search?q=hollow+knight&rlz=1C1VDKB_enUS989US989&sxsrf=ALiCzsamv5U12FoyzAg2LYh' \
          'CvZ18J8ZtGg:1656235915178&so' \
          'urce=lnms&tbm=isch&sa=X&ved=2ahUKEwjquo3L58r4AhWjDkQIHXtZDbgQ_AUoAnoECAEQBA&biw=953&bih=1077&dpr=0.8'
    fetcher = WebscraperFetcher(url, count)
    fetcher.fetch_to_dir(local_dir)

    #TODO: set up an engine + figure out better way to give url's


if __name__ == "__main__":
    run(main)
