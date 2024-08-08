from typing import List, TypedDict, Optional
from datetime import datetime

class Article(TypedDict):
    feedId: Optional[str]
    title: Optional[str]
    language: Optional[str]
    url: Optional[str]
    pub_date: Optional[datetime]
    created: Optional[int]
    authors: Optional[str]
    summary: Optional[str]
    text: Optional[str]

class ClassifiedArticle(TypedDict):
    feedId: Optional[str]
    title: Optional[str]
    language: Optional[str]
    url: Optional[str]
    pub_date: Optional[datetime]
    created: Optional[int]
    authors: Optional[str]
    summary: Optional[str]
    text: Optional[str]
    category: Optional[str]
    crime: Optional[List[str]]
    event_chance: int
    blocked_content: bool

# 'feedId', 'title', 'language', 'url', 'pub_date', 'created', 'authors', 'summary', 'text'
class CsvData(TypedDict):
    feedId: str
    title: str
    language: str
    url: str
    pub_date: str
    created: str
    authors: Optional[str]
    summary: Optional[str]
    text: Optional[str]
    text: Optional[str]