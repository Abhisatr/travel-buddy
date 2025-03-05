from fpdf import FPDF

class PDFGenerator:
    @staticmethod
    def create(itinerary, city, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Travel Itinerary for {city}", ln=1, align="C")
        for day, schedule in itinerary.items():
            pdf.cell(200, 10, txt=day, ln=1)
            for time, loc in schedule.items():
                pdf.cell(200, 10, txt=f"{time}: {loc}", ln=1)
        pdf.output(filename)
