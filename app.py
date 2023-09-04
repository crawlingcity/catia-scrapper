from flask import Flask, request, render_template
import scrap  # Import your script here, rename `scrap` to the actual name of your script file

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error_message = ""

    try:
        if request.method == "POST":
            url = "https://www.dgae.medu.pt/informacao-consolidada/listas/reserva-de-recrutamento-no-01"
            download_folder = "/tmp"  # Temporary folder to store downloaded files
            code = request.form.get("code")

            if not code:
                raise ValueError("O código está vazio. Por favor, insira um código.")

            results = list(
                scrap.find_code_in_pdfs(
                    scrap.download_pdfs(scrap.get_pdf_urls(url), download_folder), code
                )
            )
    except Exception as e:
        error_message = str(e)

    return render_template("index.html", results=results, error_message=error_message)


if __name__ == "__main__":
    app.run(debug=True)
