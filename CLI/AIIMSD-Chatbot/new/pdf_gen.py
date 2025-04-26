def generate_pdf(patient_data,report)->None:
    from fpdf import FPDF
    class PDf(FPDF):
        def header(self):
            self.set_font('helvetica','BU',26)
            self.cell(190,30,"REPORT",ln=True,align="C")
            self.ln(20)
        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica','',14)
            self.cell(0,10,f"page{self.page_no()}/{{nb}}",align="C")
    pdf=PDf('p','mm','A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=1,margin=15)
    summary=report.split("\n\n")

    #name
    pdf.set_font('helvetica','B',16)
    pdf.cell(30,15,'Name:',align="L")
    pdf.set_font('helvetica','',16)
    pdf.cell(20,15,f"{patient_data['name']}",ln=True)
    #age
    pdf.set_font('helvetica','B',16)
    pdf.cell(30,15,'Age:',align="L")
    pdf.set_font('helvetica','',16)
    pdf.cell(20,15,f"{patient_data['age']}",ln=True)
    #gender
    pdf.set_font('helvetica','B',16)
    pdf.cell(30,15,'Gender:',align="L")
    pdf.set_font('helvetica','',16)
    pdf.cell(20,15,f"{patient_data['gender']}",ln=True)           
    #summary
    pdf.set_font('helvetica','B',16)
    pdf.cell(30,15,'Summary:',align="L")
    pdf.set_font('helvetica','',16)
    pdf.multi_cell(150,10,summary[len(summary)-1])  

    pdf.output("patient_report.pdf")
    print("The pdf have been generated kindly check")
    return

# generate_pdf(patient_data,report)