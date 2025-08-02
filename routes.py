from flask import render_template, jsonify, request
from app import app
from crawler import AcademicCrawler
from data_processor import DataProcessor
import threading
import logging

logger = logging.getLogger(__name__)

# Global variables for crawling status
crawling_status = {
    'is_running': False,
    'progress': 0,
    'message': 'جاهز للبدء',
    'total_extracted': 0
}

@app.route('/')
def index():
    """Main page with Arabic interface"""
    data_processor = DataProcessor()
    stats = data_processor.get_statistics()
    sample_data = data_processor.export_sample_data(5)
    
    return render_template('index.html', 
                         stats=stats, 
                         sample_data=sample_data,
                         crawling_status=crawling_status)

@app.route('/start_crawling', methods=['POST'])
def start_crawling():
    """Start the crawling process"""
    global crawling_status
    
    if crawling_status['is_running']:
        return jsonify({'error': 'الزحف قيد التشغيل بالفعل'}), 400
    
    target_count = request.json.get('target_count', 290000)
    
    def crawl_background():
        global crawling_status
        try:
            crawling_status = {
                'is_running': True,
                'progress': 0,
                'message': 'بدء عملية الزحف...',
                'total_extracted': 0
            }
            
            crawler = AcademicCrawler()
            data_processor = DataProcessor()
            
            crawling_status['message'] = 'جاري استخراج البيانات من المصادر الأكاديمية...'
            crawling_status['progress'] = 10
            
            # Start crawling
            crawled_data = crawler.crawl_all_sources(target_count)
            
            crawling_status['message'] = 'جاري حفظ البيانات في قاعدة البيانات...'
            crawling_status['progress'] = 80
            
            # Save to database
            saved_count, errors = data_processor.save_to_database(crawled_data)
            
            crawling_status = {
                'is_running': False,
                'progress': 100,
                'message': f'تم بنجاح! تم استخراج وحفظ {saved_count} عنصر',
                'total_extracted': saved_count
            }
            
            if errors:
                logger.warning(f"Crawling completed with {len(errors)} errors")
            
        except Exception as e:
            logger.error(f"Crawling error: {e}")
            crawling_status = {
                'is_running': False,
                'progress': 0,
                'message': f'خطأ في عملية الزحف: {str(e)}',
                'total_extracted': 0
            }
    
    # Start crawling in background thread
    thread = threading.Thread(target=crawl_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'تم بدء عملية الزحف بنجاح'})

@app.route('/crawling_status')
def get_crawling_status():
    """Get current crawling status"""
    return jsonify(crawling_status)

@app.route('/api/data')
def get_all_data():
    """API endpoint to get all extracted data as JSON"""
    data_processor = DataProcessor()
    all_data = data_processor.get_all_data_as_json()
    return jsonify(all_data)

@app.route('/api/data/sample')
def get_sample_data():
    """API endpoint to get sample data"""
    limit = request.args.get('limit', 10, type=int)
    data_processor = DataProcessor()
    sample_data = data_processor.export_sample_data(limit)
    return jsonify(sample_data)

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get crawling statistics"""
    data_processor = DataProcessor()
    stats = data_processor.get_statistics()
    return jsonify(stats)

@app.route('/api/data/field/<field>')
def get_data_by_field(field):
    """Get data filtered by scientific field"""
    from models import AcademicContent
    try:
        filtered_data = AcademicContent.query.filter_by(field=field).all()
        json_data = [item.to_dict() for item in filtered_data]
        return jsonify(json_data)
    except Exception as e:
        logger.error(f"Error filtering by field {field}: {e}")
        return jsonify({'error': 'خطأ في استرجاع البيانات'}), 500

@app.route('/all-data')
def all_data():
    """Display all academic data with pagination and filters"""
    from models import AcademicContent
    from app import db
    import json
    
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 24  # Items per page
        
        # Get filter parameters
        search_query = request.args.get('search', '').strip()
        field_filter = request.args.get('field', '').strip()
        type_filter = request.args.get('type', '').strip()
        
        # Build query
        query = AcademicContent.query
        
        # Apply search filter (case insensitive)
        if search_query:
            query = query.filter(
                (AcademicContent.title.contains(search_query)) |
                (AcademicContent.summary.contains(search_query)) |
                (AcademicContent.field.contains(search_query))
            )
        
        # Apply field filter
        if field_filter:
            query = query.filter(AcademicContent.field == field_filter)
            
        # Apply type filter
        if type_filter:
            query = query.filter(AcademicContent.type == type_filter)
        
        # Order by date (newest first) then by id
        query = query.order_by(AcademicContent.date.desc(), AcademicContent.id.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        items = pagination.items
        
        # Process items for template
        processed_items = []
        for item in items:
            processed_item = {
                'id': item.id,
                'type': item.type,
                'title': item.title,
                'field': item.field,
                'date': item.date,
                'location': item.location,
                'summary': item.summary,
                'source_url': item.source_url,
                'crawled_at': item.crawled_at,
                'key_people_list': json.loads(item.key_people) if item.key_people else [],
                'verified_facts_list': json.loads(item.verified_facts) if item.verified_facts else []
            }
            processed_items.append(processed_item)
        
        # Get unique fields and types for filters
        fields = db.session.query(AcademicContent.field.distinct()).all()
        fields = [field[0] for field in fields]
        
        types = db.session.query(AcademicContent.type.distinct()).all()
        types = [type_[0] for type_ in types]
        
        # Get total count
        total_count = AcademicContent.query.count()
        
        return render_template('all_data.html',
                             items=processed_items,
                             pagination=pagination,
                             fields=sorted(fields),
                             types=sorted(types),
                             total_count=total_count)
        
    except Exception as e:
        logger.error(f"Error in all_data route: {str(e)}")
        return render_template('all_data.html',
                             items=[],
                             pagination=None,
                             fields=[],
                             types=[],
                             total_count=0,
                             error=str(e))

@app.route('/download_json')
def download_json():
    """Download all data as JSON file"""
    from flask import Response
    import json
    
    data_processor = DataProcessor()
    all_data = data_processor.get_all_data_as_json()
    
    json_output = json.dumps(all_data, ensure_ascii=False, indent=2)
    
    return Response(
        json_output,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=academic_data.json'}
    )
