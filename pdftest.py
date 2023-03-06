# =========================
# Author: Kai Leon Deines
# =========================
import pdfkit


def convert_to_pdf():
    pdf = pdfkit.from_file(["out/output.html"], "out/output.pdf")
