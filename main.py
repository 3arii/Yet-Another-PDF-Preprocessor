import re
import string
import json
from collections import Counter
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from stopwords import get_stopwords
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar

# Load the Turkish BERT NER model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("akdeniz27/bert-base-turkish-cased-ner")
model = AutoModelForTokenClassification.from_pretrained("akdeniz27/bert-base-turkish-cased-ner")
ner_pipeline = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=0)

# Load Turkish stopwords
turkish_stopwords = get_stopwords("turkish")

def extract_text_with_font_size(pdf_file):
    text_blocks = []
    font_sizes = []
    
    for page_layout in extract_pages(pdf_file):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        text = text_line.get_text()  # Get the entire text line
                        font_size = None
                        for char in text_line:
                            if isinstance(char, LTChar):
                                font_size = char.size  # Get font size from any character
                                break
                        if font_size is not None:
                            text_blocks.append({'text': text.strip(), 'font_size': font_size})
                            font_sizes.append(font_size)
    
    print(f"Extracted font sizes: {font_sizes}")  # Debugging output
    return text_blocks, font_sizes

def calculate_average_font_size(font_sizes):
    if not font_sizes:
        print("No font sizes found, returning default value") 
        return None 
    return sum(font_sizes) / len(font_sizes)

def filter_by_average_font_size(text_blocks, average_font_size):
    if average_font_size is None:
        return '' 
    filtered_text = ' '.join([block['text'] for block in text_blocks if abs(block['font_size'] - average_font_size) <= 1])
    return filtered_text

def remove_emails(text):
    return re.sub(r'\S+@\S+', '', text)

def remove_numbers(text):
    return re.sub(r'\d+', '', text)

def clean_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def normalize_text(text):
    return text.lower().strip()

def remove_stopwords(text):
    tokens = text.split()
    cleaned_text = " ".join([word for word in tokens if word.lower() not in turkish_stopwords])
    return cleaned_text

def remove_named_entities(text, labels_to_remove=['B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC']):
    ner_results = ner_pipeline(text)

    for entity in ner_results:
        if entity['entity_group'] in labels_to_remove:
            text = text.replace(entity['word'], '')
    return text


def remove_repeated_patterns(text, pattern):
    return re.sub(pattern, '', text)


def clean_pdf_document(pdf_file, header_pattern=None):
    text_blocks, font_sizes = extract_text_with_font_size(pdf_file)
    
    average_font_size = calculate_average_font_size(font_sizes)
    
    text = filter_by_average_font_size(text_blocks, average_font_size)
    
    if not text:
        print("No text found after filtering by font size")  # Debugging line
        return ''  
    
    text = remove_emails(text)
    text = remove_numbers(text)
    
    if header_pattern:
        text = remove_repeated_patterns(text, header_pattern)
    
    text = clean_punctuation(text)
    text = normalize_text(text)
    text = remove_stopwords(text)
    
    text = remove_named_entities(text, labels_to_remove=['B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC'])
    
    return text

def save_to_jsonl(file_name, text):
    with open(file_name, 'a', encoding='utf-8') as f:
        json.dump({"processed_text": text}, f, ensure_ascii=False)
        f.write('\n')

if __name__ == '__main__':
    pdf_file = 'temp.pdf'
    
    header_pattern = r'Repeating Header Text'

    clean_text = clean_pdf_document(pdf_file, header_pattern=header_pattern)
    
    if clean_text:
        save_to_jsonl('processed_financial_report.jsonl', clean_text)
    else:
        print("No text to save.")

    print("Text has been successfully saved to JSONL format.")