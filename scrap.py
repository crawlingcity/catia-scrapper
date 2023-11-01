import os
import re
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
import urllib3

urllib3.disable_warnings()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

CHUNK_SIZE = 1024


def get_most_recent_link(url):
    response = session.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the q-expansion-item containing the label "Listas"
    listas_section = soup.find('q-expansion-item', label='Listas')

    # Find the first link under the "Listas" section (assuming it's the most recent link)
    most_recent_link = listas_section.find('a') if listas_section else None

    # Extracting the text and URL of the most recent link (if found)
    most_recent_link_text = most_recent_link.get_text(strip=True) if most_recent_link else None
    most_recent_link_url = most_recent_link['href'] if most_recent_link else None

    return most_recent_link_text, most_recent_link_url

def get_pdf_urls(url):

    response = session.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return [a["href"] for a in soup.select('a[href$=".pdf"]')]

def download_pdfs(pdf_urls, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    file_url_mapping = {}

    def download(url):
        response = session.get(url, verify=False)
        file_name = os.path.join(download_folder, url.split("/")[-1])
        with open(file_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                file.write(chunk)
        file_url_mapping[file_name] = url

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(download, pdf_urls)

    return file_url_mapping

def find_code_in_pdfs(file_url_mapping, code):
    results = []

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
            found_instances = page.search_for(code)
            if found_instances:
                text_instances = [page.get_textbox(rect) for rect in found_instances]
                for text_instance in text_instances:
                    results.append((url, page_number, text_instance, lista_line))
                break

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_item, file_url_mapping.items())

    return results

def main(download_folder, code):
    base_url = "https://www.dgae.medu.pt/"
    url = "https://www.dgae.medu.pt/informacao-consolidada/reserva-de-recrutamento"
    download_folder = os.path.expanduser(download_folder)

    # Get the most recent link dynamically
    most_recent_link_text, most_recent_link_url = get_most_recent_link(url)
    if not most_recent_link_url:
        print("Could not find the most recent link. Exiting.")
        return

    # Get the PDF URLs from the most recent link
    pdf_urls = get_pdf_urls(base_url + most_recent_link_url)

    file_url_mapping = download_pdfs(pdf_urls, download_folder)
    for url, page, text_instance, lista_line in find_code_in_pdfs(file_url_mapping, code):
        print(f"{'-'*80}")
        print(f"URL do Ficheiro: {url}")
        print(f"Página: {page}")
        print(f"Código: {code}")
        # print(f"Texto Encontrado: {text_instance}")
        print(f"LISTA: {lista_line}")
        print(f"{'-'*80}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape, download and search PDFs")
    parser.add_argument("download_folder", help="Folder to download PDFs")
    parser.add_argument("code", help="Code to search for")

    args = parser.parse_args()
    main(args.download_folder, args.code)
