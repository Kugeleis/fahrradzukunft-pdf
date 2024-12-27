from pathlib import Path
from bs4 import BeautifulSoup
import requests
from weasyprint import HTML, CSS
from urllib.parse import urljoin, urlparse
import yaml


def collect_links(start_url):
    """collect all links from a given URL below it"""
    # Send a GET request to the starting URL
    response = requests.get(start_url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract all anchor tags
    anchor_tags = soup.find_all("a", href=True)

    # Filter links that start with the specified pattern
    start_url_parsed = urlparse(start_url)
    base_url = f"{start_url_parsed.scheme}://{start_url_parsed.netloc}"
    filtered_links = set()

    for tag in anchor_tags:
        href = tag["href"]
        full_url = urljoin(base_url, href)
        if full_url.startswith(start_url):
            filtered_links.add(full_url)

    return filtered_links


def collect_ordered_list_links(start_url):
    # Send a GET request to the starting URL
    response = requests.get(start_url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the <ol> within the specified path
    ol_tag = soup.select_one("body > div.seite > div > div > nav.ausgabe > ol")

    if not ol_tag:
        return []

    # Extract all anchor tags within the <ol>
    anchor_tags = ol_tag.find_all("a", href=True)

    # Collect the links
    base_url = response.url
    links = [urljoin(base_url, tag["href"]) for tag in anchor_tags]

    return links


def save_links_to_yaml(links: list[str], file_path: Path):
    """save links to a YAML file"""
    data = {"links": list(links)}
    with open(file_path, "w") as file:
        yaml.dump(data, file)

def get_page_text(url) -> str:
    """get the text content of the webpage"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    main_content = soup.find("main")
    if not main_content:
        raise ValueError("No <main> tag found in the webpage.")
    return str(main_content)


def create_file_name(url: str) -> str:
    """create a file name from the URL"""
    parts = url.rstrip('/').split('/')
    return parts[-1] + ".pdf"


def make_pdf(url: str, data_dir: Path, css) -> None:
    """create a PDF from the webpage"""
    main_html = get_page_text(url)
    file_name = create_file_name(url)
    file_path = data_dir / file_name
    # Render the <main> content as a PDF
    HTML(string=main_html, base_url=url).write_pdf(
        file_path,
        stylesheets=[CSS(string=css)],
        optimize_images=True,
        jpeg_quality=60,
        dpi=300,
        zoom=0.8,
    )

def create_foo_bar_string(url: str) -> str:
    """Extract the domain name and the first sub-path from a URL and format it as a foo_bar string."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split('.')[-2]
    first_sub_path = parsed_url.path.strip('/').split('/')[0]
    return f"{domain}_{first_sub_path}"