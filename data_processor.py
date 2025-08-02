import json
import logging
from models import AcademicContent, CrawlStatus
from app import db
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        pass
    
    def save_to_database(self, crawled_data, source_domain="multiple"):
        """Save crawled data to database"""
        saved_count = 0
        errors = []
        
        try:
            for item in crawled_data:
                try:
                    # Check if item already exists
                    existing = AcademicContent.query.filter_by(
                        title=item['title'],
                        field=item['field']
                    ).first()
                    
                    if existing:
                        continue  # Skip duplicates
                    
                    academic_content = AcademicContent(
                        type=item['type'],
                        title=item['title'],
                        field=item['field'],
                        date=item.get('date', ''),
                        location=item.get('location', ''),
                        key_people=json.dumps(item.get('key_people', []), ensure_ascii=False),
                        summary=item['summary'],
                        verified_facts=json.dumps(item.get('verified_facts', []), ensure_ascii=False),
                        source_url=item.get('source_url', ''),
                        crawled_at=datetime.utcnow()
                    )
                    
                    db.session.add(academic_content)
                    saved_count += 1
                    
                    # Commit in batches
                    if saved_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"Saved {saved_count} items so far")
                        
                except Exception as e:
                    errors.append(f"Error saving item '{item.get('title', 'Unknown')}': {e}")
                    logger.error(f"Error saving item: {e}")
            
            # Final commit
            db.session.commit()
            
            # Update crawl status
            self.update_crawl_status(source_domain, saved_count, "completed")
            
            logger.info(f"Successfully saved {saved_count} items to database")
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Database error: {e}"
            self.update_crawl_status(source_domain, 0, "error", error_msg)
            raise e
        
        return saved_count, errors
    
    def update_crawl_status(self, domain, item_count, status, error_message=None):
        """Update or create crawl status record"""
        try:
            crawl_status = CrawlStatus.query.filter_by(source_domain=domain).first()
            
            if crawl_status:
                crawl_status.last_crawled = datetime.utcnow()
                crawl_status.total_items = item_count
                crawl_status.status = status
                crawl_status.error_message = error_message
            else:
                crawl_status = CrawlStatus(
                    source_domain=domain,
                    last_crawled=datetime.utcnow(),
                    total_items=item_count,
                    status=status,
                    error_message=error_message
                )
                db.session.add(crawl_status)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating crawl status: {e}")
            db.session.rollback()
    
    def get_all_data_as_json(self):
        """Retrieve all academic content as JSON"""
        try:
            all_content = AcademicContent.query.all()
            json_data = [item.to_dict() for item in all_content]
            return json_data
        except Exception as e:
            logger.error(f"Error retrieving data as JSON: {e}")
            return []
    
    def get_statistics(self):
        """Get crawling and data statistics"""
        try:
            total_items = AcademicContent.query.count()
            
            # Count by field
            field_counts = db.session.query(
                AcademicContent.field,
                db.func.count(AcademicContent.id)
            ).group_by(AcademicContent.field).all()
            
            # Count by type
            type_counts = db.session.query(
                AcademicContent.type,
                db.func.count(AcademicContent.id)
            ).group_by(AcademicContent.type).all()
            
            # Get crawl status
            crawl_statuses = CrawlStatus.query.all()
            
            return {
                'total_items': total_items,
                'field_distribution': dict(field_counts),
                'type_distribution': dict(type_counts),
                'crawl_statuses': [
                    {
                        'domain': status.source_domain,
                        'last_crawled': status.last_crawled.isoformat() if status.last_crawled else None,
                        'total_items': status.total_items,
                        'status': status.status
                    } for status in crawl_statuses
                ]
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'total_items': 0, 'field_distribution': {}, 'type_distribution': {}, 'crawl_statuses': []}
    
    def export_sample_data(self, limit=10):
        """Export a sample of data for demonstration"""
        try:
            sample_content = AcademicContent.query.limit(limit).all()
            return [item.to_dict() for item in sample_content]
        except Exception as e:
            logger.error(f"Error exporting sample data: {e}")
            return []
