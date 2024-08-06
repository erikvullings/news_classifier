import csv
from datetime import datetime, timedelta, timezone
import os
import weaviate
from weaviate.classes.query import Filter
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def write_to_csv(file, articles, write_header=False):
    fieldnames = ['feedId', 'title', 'language', 'url', 'pub_date', 'created', 'authors', 'summary', 'text']
    
    with open(file, mode='a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, escapechar='\\', delimiter=";")
        
        if write_header:
            writer.writerow(fieldnames)
        
        for article in articles:
            writers = article.properties.get('authors', [])
            authors_string = ', '.join(writers) if writers else ''
            
            row = [
                article.properties.get('feedId', ''),
                article.properties.get('title', ''),
                article.properties.get('language', ''),
                article.properties.get('url', ''),
                article.properties.get('pub_date').isoformat() if isinstance(article.properties.get('pub_date'), datetime) else article.properties.get('pub_date', ''),
                article.properties.get('created', ''),
                authors_string,
                escape_csv_field(article.properties.get('summary', '')),
                escape_csv_field(article.properties.get('text', '')),
            ]
            writer.writerow(row)


def escape_csv_field(text):
    """
    Escapes special characters in a text field for CSV format.
    
    Args:
        text (str): The text to be escaped.
        
    Returns:
        str: The escaped text.
    """
    text = "\n".join([line for line in text.splitlines() if line.strip() != ""])
    # Replace double quotes with two double quotes
    escaped_text = text.replace('"', '""')
    return f'"{escaped_text}"'


def date_iterator(start_date, end_date):
    """
    Generator that yields dates starting from start_date to end_date, incremented by 6 hours.
    
    :param start_date: The date to start from (inclusive).
    :param end_date: The date to stop at (exclusive).
    """
    # Ensure the start and end dates are timezone-aware and set to UTC
    start_date = start_date.replace(tzinfo=timezone.utc)
    end_date = end_date.replace(tzinfo=timezone.utc)

    current_date = start_date
    while True:
        if current_date < end_date:
            yield current_date
            current_date += timedelta(hours=6)
        else:
            yield end_date


def main() -> None:
    server = os.getenv('SERVER') or "localhost"
    client = weaviate.connect_to_custom(
        http_host=server,
        http_port="8889",
        http_secure=False,
        grpc_port="50051",
        grpc_host=server,
        grpc_secure=False,
    )
    Article = client.collections.get("Article")
    max_count = 1000000
    count = 0
    csv_file = 'data/articles_export.csv'

    start_date = datetime(2024, 3, 14, 0, 0, 0, 0)
    end_date = datetime.now()
    date_generator  = date_iterator(start_date=start_date, end_date=end_date)
    from_date = next(date_generator)
    till_date = next(date_generator)

    # Write the header only once at the beginning
    write_to_csv(csv_file, [], write_header=True)

    while count < max_count:
        if from_date >= till_date:
            print("Done processing articles")
            break

        print(f"Processing articles from {from_date} till {till_date}")

        articles = Article.query.fetch_objects(
            limit=10000,
            include_vector=False,
            return_properties=['feedId', 'title', 'language', 'url', 'pub_date', 'created', 'authors', 'summary', 'text'],
            filters=Filter.all_of([Filter.by_property(name="created").greater_or_equal(val=int(from_date.timestamp())),Filter.by_property(name="created").less_than(val=int(till_date.timestamp()))]),
        )
        
        from_date = till_date
        till_date = next(date_generator)
        
        if not articles.objects:
            print("No articles to fetch")
            continue

        write_to_csv(csv_file, articles.objects)
        
        count += len(articles.objects)
        print(f"Total articles processed: {count}")
        
    print(f"Export complete. {count} articles written to {csv_file}")
    client.close()

if __name__ == '__main__':
    main()