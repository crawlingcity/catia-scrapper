import os
import re
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import requests
import argparse
import urllib3
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

session = requests.Session()


def get_pdf_urls(url):
    response = session.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return [
        a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")
    ]


def download_pdfs(pdf_urls, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    file_url_mapping = {}

    def download(url):
        response = session.get(url, verify=False)
        file_name = os.path.join(download_folder, url.split("/")[-1])
        with open(file_name, "wb") as file:
            file.write(response.content)
        file_url_mapping[file_name] = url

    with ThreadPoolExecutor() as executor:
        executor.map(download, pdf_urls)

    return file_url_mapping


def find_code_in_pdfs(file_url_mapping, code):
    results = []
    pattern = re.compile(rf"{code}([\s\S]*?)(?=\d|$)")

    def process_item(item):
        file_path, url = item
        doc = fitz.open(file_path)
        lista_line = ""
        first_page_text = doc[0].get_text()
        for line in first_page_text.split('\n'):
            if "LISTA" in line:
                lista_line = line
                break

        for page_number, page in enumerate(doc, start=1):
            text = page.get_text()
            match = pattern.search(text)
            if match:
                full_line = match.group(0)
                name_lines = match.group(1).strip().split('\n')
                name_line = ' '.join(name_lines[1:]) if len(name_lines) > 1 else name_lines[0]
                results.append((url, page_number, full_line, lista_line, name_line))
                break

    with ThreadPoolExecutor() as executor:
        executor.map(process_item, file_url_mapping.items())

    return results

def main(url, download_folder, code):
    download_folder = os.path.expanduser(download_folder)
    pdf_urls = get_pdf_urls(url)
    file_url_mapping = download_pdfs(pdf_urls, download_folder)
    for url, page, line, lista_line, name_line in find_code_in_pdfs(
        file_url_mapping, code
    ):
        print(f"{'-'*80}")
        print(f"URL do Ficheiro: {url}")
        print(f"Página: {page}")
        print(f"Código: {code}")
        print(f"Nome: {name_line}")
        print(f"LISTA: {lista_line}")
        print(f"{'-'*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape, download and search PDFs")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("download_folder", help="Folder to download PDFs")
    parser.add_argument("code", help="Code to search for")

    args = parser.parse_args()
    main(args.url, args.download_folder, args.code)


# cli usage
# python3 scrap.py "https://www.dgae.medu.pt/informacao-consolidada/listas/reserva-de-recrutamento-no-01" "/tmp" "8047179446"
