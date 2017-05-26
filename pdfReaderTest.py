import PyPDF2

fileName = "fileBQADAQADAgADnhU4R_ZsMn3PhImLAg.pdf"
pdfFileObj = open(fileName,"rb")
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
pageObj = pdfReader.getPage(0)
page1 = pageObj.extractText()
message_text = page1.encode('utf-8')
page1.split(' ')
