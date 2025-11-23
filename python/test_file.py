from pdf_parser import extract_pdf_text

# Test with a single PDF URL
pdf_url = "https://www.etenders.gov.ie/epps/cft/downloadNoticeForAdvSearch.do?resourceId=5196306"

result = extract_pdf_text(pdf_url)

# Write the extracted text to a file
output_filename = "extracted_pdf_text.txt"
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(f"PDF URL: {result['pdf_url']}\n")
    f.write("="*50 + "\n")
    f.write("EXTRACTED TEXT:\n")
    f.write("="*50 + "\n\n")
    f.write(result['text_content'])

print(f"Text extracted and saved to {output_filename}")