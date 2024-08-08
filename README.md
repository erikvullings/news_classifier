# Developing a classifier using LLMs

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with the following variables: `SERVER`. See `example.env` for an example.


## Prompts

**System Prompt:**

Welcome to the News Article Categorization System!

This system helps you categorize news articles based on their content. Please follow the instructions below to classify each article.

1. Choose a category from the list of generic categories ( Politics, Business, Sports, Entertainment, Health, Science, Technology, Education, Environment, Society & Culture ) that best describes the article's topic.
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
3. Indicate the chance that the article contains information about an event (location, date, type, name, etc.) using one of the following scales:
	* 1: The article is unlikely to contain any specific details.
	* 2: The article may contain some general details or a brief summary.
	* 3: The article contains more detailed information about an event, such as location and date.
	* 4: The article provides comprehensive coverage of an event.

**User Prompt:**

Please categorize the news article below:

```json
{
  "article_title": "",
  "article_content": "",
  "generic_category": "",
  "crime_categories": [""],
  "event_chance": ""
}
```

Replace each placeholder with your response. The `generic_category` field should be one of the generic categories listed above, and the `crime_categories` field should be a list containing one or more crime categories as needed.

Example:

```json
{
  "article_title": "Breaking News: Police Investigate Robbery",
  "article_content": "The police are investigating a robbery that occurred at a local convenience store.",
  "generic_category": "Crime",
  "crime_categories": ["Violent Crime"],
  "event_chance": 3
}
```