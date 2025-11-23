import anthropic
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

def parse_pdf_with_claude(text_content):
    """Parse PDF text using Claude API"""
    
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    
    prompt = """Extract the following fields from this tender PDF text and return ONLY valid JSON with no markdown formatting:
{
  "procedure_id": "",
  "title": "",
  "buyer_name": "",
  "buyer_country": "",
  "estimated_value": "",
  "start_date": "",
  "duration_months": "",
  "submission_deadline": "",
  "main_classification": "",
  "lots": []
}

For lots array, extract each lot with: lot_id, title, and estimated_value.

PDF Text:
""" + text_content
    
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Get the response text
    response_text = message.content[0].text
    
    # Debug: print the raw response
    print("Raw Claude response:")
    print(response_text)
    print("\n" + "="*50 + "\n")
    
    # Remove markdown code blocks if present
    json_text = re.sub(r'^```json\s*\n', '', response_text)
    json_text = re.sub(r'\n```\s*$', '', json_text)
    json_text = re.sub(r'^```\s*\n', '', json_text)
    json_text = json_text.strip()
    
    return json.loads(json_text)

def parse_pdf_file(filepath):
    """Read PDF text file and parse with Claude"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Remove the header info we added
        text_content = content.split("EXTRACTED TEXT:\n==================================================\n\n", 1)[1]
    
    return parse_pdf_with_claude(text_content)

if __name__ == "__main__":
    # Parse the extracted PDF text
    result = parse_pdf_file("extracted_pdf_text.txt")
    
    # Print formatted JSON
    print(json.dumps(result, indent=2))
    
    # Save to file
    with open("parsed_tender_data.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print("\nParsed data saved to parsed_tender_data.json")