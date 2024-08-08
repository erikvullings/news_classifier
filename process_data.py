import csv
from datetime import datetime
import json
from typing import List
from models import CsvData, ClassifiedArticle
from text_analysis import analyze_responses, analyze_responses_ollama

use_ollama = True
model = "gpt-35-turbo"

def read_csv_file(file_path: str) -> List[CsvData]:
    csv.field_size_limit(max(csv.field_size_limit(), 1024 * 1024 * 10))  # Increase the field size limit to 10MB
    csv_data = []
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            csv_data.append(CsvData(**row))
            if len(csv_data) > 25000:
                break
    return csv_data

def process_data(file_path: str) -> List[ClassifiedArticle]:
    csv_data = read_csv_file(file_path)
    start_time = datetime.now()
    
    results = []
    for article in csv_data:
        title = article['title'].strip('"')
        text = (article['summary'] or article['text']).strip('"')
        
        if use_ollama:
            classified_article = analyze_responses_ollama(title, text)
        else:
            classified_article = analyze_responses(title, text, model)
        
        # Add missing fields from the original CsvData
        classified_article['authors'] = article['authors']
        classified_article['created'] = article['created']
        classified_article['title'] = article['title'].strip('"')
        classified_article['text'] = article['text'].strip('"')
        classified_article['summary'] = article['summary'].strip('"')
        classified_article['pub_date'] = article['pub_date']
        classified_article['feedId'] = article['feedId']
        classified_article['language'] = article['language']
        
        results.append(classified_article)
        delta = (datetime.now() - start_time).seconds
        print(f"Processing item", len(results), "in", delta/len(results), "msg/sec.")
    
    return results

def save_as_json(data: List[ClassifiedArticle], file_path: str):
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)


def save_as_csv(data: List[ClassifiedArticle], file_path: str):
    fieldnames = ['feedId', 'title', 'language', 'url', 'pub_date', 'created', 'authors', 'summary', 'text', 'generic_category', 'crime_categories', 'event_chance', 'inaccessible', 'explanation']
    
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for item in data:
            writer.writerow(item)

def main():
    input_file = "data/articles_export.csv"
    # input_file = "data/articles_extract.csv"
    if use_ollama:
        output_json = "data/analysis_output_ollama.json"
        output_csv = "data/analysis_output_ollama.csv"
    else:
        output_json = format(f"data/analysis_output_{model}.json")
        output_csv = format(f"data/analysis_output_{model}.csv")
    
    results = process_data(input_file)
    save_as_json(results, output_json)
    save_as_csv(results, output_csv)
    
    print(f"Processing complete. Results saved to {output_json} and {output_csv}")

if __name__ == "__main__":
    main()