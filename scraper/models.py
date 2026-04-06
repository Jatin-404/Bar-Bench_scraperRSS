from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleResult(BaseModel):
    url: str
    title: str
    published: Optional[str]   # raw string from RSS; parse later if needed
    author: Optional[str]
    category: Optional[str]
    full_text: str             # cleaned body text, paragraphs joined by \n\n

    def model_post_init(self, __context):
        # auto-populate char_count after init
        object.__setattr__(self, "char_count", len(self.full_text))