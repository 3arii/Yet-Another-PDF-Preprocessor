from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar

def extract_text_with_font_size(pdf_file):
    text_blocks = []
    
    # Iterate through the pages of the PDF
    for page_layout in extract_pages(pdf_file):
        # Iterate through the elements in the layout
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                # Iterate through the text lines in the element
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        words = text_line.get_text().split()  # Get words from the text line
                        font_size = None
                        # Iterate through the characters in the text line to get the font size
                        for char in text_line:
                            if isinstance(char, LTChar):
                                font_size = char.size  # Get font size from any character
                                break
                        if font_size is not None:
                            for word in words:
                                text_blocks.append({'text': word, 'font_size': font_size})
    
    return text_blocks

def extract_last_100_words_with_font_size(text_blocks):
    # Get the last 100 words from the text blocks
    last_100_blocks = text_blocks[-100:]
    
    # Calculate the average font size for the last 100 words
    if last_100_blocks:
        avg_font_size_last_100 = sum(block['font_size'] for block in last_100_blocks) / len(last_100_blocks)
    else:
        avg_font_size_last_100 = 0
    
    return last_100_blocks, avg_font_size_last_100

def calculate_average_font_size(text_blocks):
    # Calculate the average font size for the entire document
    if text_blocks:
        avg_font_size = sum(block['font_size'] for block in text_blocks) / len(text_blocks)
    else:
        avg_font_size = 0
    
    return avg_font_size

# Example usage of the program
if __name__ == '__main__':
    # Provide the PDF file path here
    pdf_file = 'temp.pdf'
    
    # Extract text with font sizes from the PDF
    text_blocks = extract_text_with_font_size(pdf_file)
    
    # Extract the last 100 words and calculate their average font size
    last_100_blocks, avg_font_size_last_100 = extract_last_100_words_with_font_size(text_blocks)
    last_100_words = ' '.join([block['text'] for block in last_100_blocks])
    
    # Calculate the average font size for the entire document
    avg_font_size = calculate_average_font_size(text_blocks)
    
    # Print the results
    if last_100_words:
        print("Last 100 words from the PDF:")
        print(last_100_words)
        print(f"Average font size of the last 100 words: {avg_font_size_last_100}")
    else:
        print("No text to display.")
    
    print(f"Average font size of the entire document: {avg_font_size}")