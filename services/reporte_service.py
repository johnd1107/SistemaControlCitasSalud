from fpdf import FPDF


class ReporteService:
    @staticmethod
    def generar_receta(paciente, diagnostico, tratamiento):
        pdf = FPDF()
        pdf.add_page()

        # Diseño Médico
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(200, 15, "CENTRO MÉDICO SALUDPLUS", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"PACIENTE: {paciente['nombre']} {paciente['apellido']}", ln=True)
        pdf.cell(200, 10, f"CÉDULA: {paciente['cedula']}", ln=True)
        pdf.ln(5)

        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, "DIAGNÓSTICO:", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 10, diagnostico, 1)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "PRESCRIPCIÓN:", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 10, tratamiento, 1)

        return pdf.output(dest='S').encode('latin-1')