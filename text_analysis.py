import json
import requests
import os
from typing import Optional
from openai import AzureOpenAI
from dotenv import load_dotenv
from models import ClassifiedArticle

# Load environment variables from the .env file
load_dotenv()

temperature = 0.1

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version=os.getenv("API_VERSION"),
)

OLLAMA_SERVER = os.getenv("OLLAMA_SERVER")

# System message
system_message = """Welcome to the News Article Categorization System!

This system helps you categorize news articles based on their content. Please follow the instructions below to classify each article.

1. Choose a category from the list of generic categories ( Crime, Politics, Business, Sports, Entertainment, Health, Science, Technology, Defence, Education, Environment, Society & Culture ) that best describes the article's topic.
2. If the article is related to crime, select one or more of the specialized crime categories. Otherwise, set it to undefined:
	* Crime: General crimes, law enforcement activities, and court cases
	* Drug Busts: Arrest or seizure of illicit substances, their transportation, sale, or possession
	* Violent Crime: Murder, assault, robbery, and other violent offenses
	* Theft & Property Crime: Theft, burglary, vandalism, and other property-related crimes
	* Cybercrime: Online crimes, such as hacking, identity theft, phishing, and other digital threats
	* Human Trafficking: Modern-day slavery, exploitation, and human trafficking
	* Arson & Fires: Fires caused by arson or other malicious intent
	* Police Investigations: Ongoing police investigations into specific crimes or cases
	* Court Cases: Court proceedings, verdicts, and sentencing related to various crimes
	* Corruption & Organized Crime: Government corruption, organized crime groups, and their activities
  * Synthetic Drugs: Manufacture, sale, possession, or use of synthetic substances designed to mimic the effects of controlled substances
3. Indicate the chance that the article contains information about a future public gathering (such as a festival or demonstration), with a specific location and specific date, the type of gathering and name) using one of the following scales:
	* 1: The article is unlikely to contain any specific details.
	* 2: The article may contain some general details or a brief summary.
	* 3: The article contains more detailed information about an event, such as location and date.
	* 4: The article provides comprehensive coverage of an event.
4. Indicate the chance that the article text is blocked by the system, i.e. the text contains security or permission warnings about accessing the text. This is a boolean choice:
	* true: The article text is blocked by the system.
	* false: The article text is not blocked by the system.
"""

# Combined user message
user_message = """Please categorize the news article below:

TITLE: `[INSERT_ARTICLE_TITLE]`,
CONTENT: `[INSERT_ARTICLE_TEXT]`,

Using the following JSON object:

{
  "generic_category": "",
  "crime_categories": [""],
  "event_chance": 1,
  "inaccessible": false,
  "explanation": ""
}

Only return the previous JSON object and no further text: Replace each placeholder with your response. 
- `generic_category`: should be one of the generic categories listed above
- `crime_categories`: should be alist containing one or more crime categories as needed. 
- `event_chance`: 1, 2, 3 or 4
- `inaccessible`: is only `true` when the text contains security or permission warnings that access to the content is prohibited, otherwise `false`. 
- `explanation`: the explanation of your responsee.

Example:

TITLE: `Breaking News: Police Investigate Robbery`,
CONTENT: `The police are investigating a robbery that occurred at a local convenience store.`,

Result:

{
  "generic_category": "Crime",
  "crime_categories": ["Violent Crime"],
  "event_chance": 0,
  "inaccessible": false,
  "explanation": "Explain your response here."
}
"""

  

# Function to make API call
def analyze_responses(title: str, text: str, model: Optional[str]) -> ClassifiedArticle:
    filled_message = user_message.replace("[INSERT_ARTICLE_TITLE]", title).replace("[INSERT_ARTICLE_TEXT]", text)

    # API call
    response = client.chat.completions.create(
        model=model or "gpt-35-turbo",
        # model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": filled_message}
        ],
        temperature=temperature
    )
    
    result = ''
    try: 
      result = response.choices[0].message.content
    except:
      result = response.choices[0].message['content']
      
    output: ClassifiedArticle
    try:
      output = json.loads(result)
    except:
      print(f("Warning: could not convert result to JSON: {result}"))
      output = analyze_responses(title, text, model)
    
    return output


def analyze_responses_ollama(title: str, text: str) -> ClassifiedArticle:
    filled_message = user_message.replace("[INSERT_ARTICLE_TITLE]", title).replace("[INSERT_ARTICLE_TEXT]", text)

    # Ollama API call
    response = requests.post(
        OLLAMA_SERVER,
        json={
            "model": "llama3.1",  # or another model available in your Ollama setup
            "prompt": f"{system_message}\n\nHuman: {filled_message}\n\nAssistant:",
            "stream": False,
            "temperature": temperature,
        }
    )
    
    if response.status_code == 200:
        result = response.json()['response']
    else:
        print(f"Error: Ollama API call failed with status code {response.status_code}")
        return ClassifiedArticle()

    output: ClassifiedArticle
    try:
        output = json.loads(result)
    except json.JSONDecodeError:
        print(f"Warning: could not convert result to JSON: {result}")
        output = analyze_responses_ollama(title, text)
    
    return output


# def save_burnout_data_to_file(json_list: list[BurnoutData], file_path):
#     """
#     Saves a list of JSON objects to a file.

#     :param json_list: List of JSON objects (dictionaries)
#     :param file_path: Path to the file where the JSON objects will be saved
#     """
#     try:
#         with open(file_path, 'w', encoding='utf-8') as file:
#             json.dump(json_list, file, ensure_ascii=False, indent=4)
#         print(f"Successfully saved JSON list to {file_path}")
#     except Exception as e:
#         print(f"An error occurred while saving JSON list to file: {e}")

# def save_burnout_data_to_csv(data: list[BurnoutData], filename: str):
#     keys = BurnoutData.__annotations__.keys()
    
#     with open(filename, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=keys)
#         writer.writeheader()
#         for item in data:
#             writer.writerow(item)

# # Example usage
# negative_response = "Het oplaaien van gemetastaseerde kanker. Serie chemokuren halverwege afgebroken en andere medicatie gekregen. Eerst nog veel pijnklachten; momenteel gaar het weer wat beter"
# positive_response = "I started a new exercise routine and it's really boosted my energy levels and mood."

# analysis = analyze_responses(negative_response, positive_response)
# print("Comprehensive Well-being Analysis:")
# print(analysis)