from app import db
from datetime import datetime
import json

class AcademicContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50))
    location = db.Column(db.String(200))
    key_people = db.Column(db.Text)  # JSON string
    summary = db.Column(db.Text)
    verified_facts = db.Column(db.Text)  # JSON string
    source_url = db.Column(db.String(500))
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'type': self.type,
            'title': self.title,
            'field': self.field,
            'date': self.date,
            'location': self.location,
            'key_people': json.loads(self.key_people) if self.key_people else [],
            'summary': self.summary,
            'verified_facts': json.loads(self.verified_facts) if self.verified_facts else []
        }

class CrawlStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_domain = db.Column(db.String(200), nullable=False)
    last_crawled = db.Column(db.DateTime, default=datetime.utcnow)
    total_items = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
