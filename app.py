from flask import Flask, request, render_template
import scrap  # Import your script here, rename `scrap` to the actual name of your script file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error_message = ""

    try:
        if request.method == "POST":
            base_url = "https://www.dgae.medu.pt/"
            url = "https://www.dgae.medu.pt/informacao-consolidada/reserva-de-recrutamento"
            download_folder = "/tmp"  # Temporary folder to store downloaded files
            code = request.form.get("code")

            if not code:
                raise ValueError("O código está vazio. Por favor, insira um código.")

            # Get the most recent link dynamically
            most_recent_link_text, most_recent_link_url = scrap.get_most_recent_link(url)
            if not most_recent_link_url:
                raise ValueError("Could not find the most recent link. Exiting.")

            # Get the PDF URLs from the most recent link
            pdf_urls = scrap.get_pdf_urls(base_url + most_recent_link_url)

            results = list(scrap.find_code_in_pdfs(scrap.download_pdfs(pdf_urls, download_folder), code))
    except Exception as e:
        error_message = str(e)

    return render_template("index.html", results=results, error_message=error_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

