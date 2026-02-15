from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os


def create_pdf(output_path: str) -> None:
    """
    Create a simple PDF and save it locally.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "Sample PDF Generated Locally")

    # Body text
    c.setFont("Helvetica", 12)
    text_lines = [
        "This PDF was created using ReportLab.",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "You can use this script to test local PDF generation",
        "before deploying to a serverless environment.",
    ]

    y_position = height - 120
    for line in text_lines:
        c.drawString(72, y_position, line)
        y_position -= 18

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, 40, "End of document")

    c.save()


if __name__ == "__main__":
    output_file = os.path.join(os.getcwd(), "test_output.pdf")
    create_pdf(output_file)
    print(f"PDF successfully created at: {output_file}")
