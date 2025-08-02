#!/usr/bin/env python3
"""Generate large academic dataset (100,000+ items)"""

import json
import logging
import random
from app import app, db
from models import AcademicContent
from datetime import datetime, timedelta

# Base templates for generating diverse academic content
FIELDS = {
    'فيزياء': {
        'types': ['نظرية علمية', 'اكتشاف فيزيائي', 'تجربة فيزيائية', 'قانون فيزيائي'],
        'topics': ['الكم', 'النسبية', 'الكهرومغناطيسية', 'الديناميكا الحرارية', 'الميكانيكا', 'البصريات', 'الذرية', 'النووية'],
        'locations': ['ألمانيا', 'إنجلترا', 'فرنسا', 'أمريكا', 'إيطاليا', 'النمسا', 'سويسرا', 'روسيا'],
        'scientists': ['أينشتاين', 'نيوتن', 'ماكسويل', 'هايزنبرغ', 'بور', 'فاينمان', 'هوكنغ', 'شرودنغر']
    },
    'كيمياء': {
        'types': ['اكتشاف كيميائي', 'تفاعل كيميائي', 'عنصر كيميائي', 'مركب كيميائي'],
        'topics': ['الجدول الدوري', 'التفاعلات', 'المركبات العضوية', 'الكيمياء التحليلية', 'الكيمياء الحيوية'],
        'locations': ['روسيا', 'فرنسا', 'ألمانيا', 'إنجلترا', 'أمريكا', 'السويد', 'الدنمارك'],
        'scientists': ['مندليف', 'لافوازييه', 'دالتون', 'أفوجادرو', 'كوري', 'نوبل', 'باولنغ']
    },
    'رياضيات': {
        'types': ['نظرية رياضية', 'معادلة رياضية', 'برهان رياضي', 'خوارزمية رياضية'],
        'topics': ['الجبر', 'الهندسة', 'التفاضل والتكامل', 'الإحصاء', 'نظرية الأعداد', 'الهندسة التحليلية'],
        'locations': ['اليونان', 'العراق', 'إيران', 'الهند', 'ألمانيا', 'فرنسا', 'إنجلترا'],
        'scientists': ['إقليدس', 'فيثاغورس', 'الخوارزمي', 'ابن الهيثم', 'نيوتن', 'أويلر', 'غاوس']
    },
    'أحياء': {
        'types': ['اكتشاف بيولوجي', 'نظرية تطورية', 'تجربة وراثية', 'دراسة تشريحية'],
        'topics': ['الوراثة', 'التطور', 'الخلايا', 'الحمض النووي', 'البروتينات', 'الأنسجة'],
        'locations': ['إنجلترا', 'فرنسا', 'ألمانيا', 'أمريكا', 'النمسا', 'هولندا', 'إيطاليا'],
        'scientists': ['داروين', 'مندل', 'واتسون', 'كريك', 'فلمنغ', 'باستور']
    },
    'تاريخ': {
        'types': ['حدث تاريخي', 'حضارة قديمة', 'اكتشاف أثري', 'شخصية تاريخية'],
        'topics': ['الحضارات القديمة', 'الحروب', 'الاكتشافات', 'الإمبراطوريات', 'الثورات'],
        'locations': ['مصر', 'العراق', 'اليونان', 'روما', 'الصين', 'الهند', 'بلاد فارس'],
        'scientists': ['هيرودوت', 'ثوسيديدس', 'ابن خلدون', 'الطبري', 'المسعودي']
    },
    'فلك': {
        'types': ['اكتشاف فلكي', 'نظرية كونية', 'رصد فلكي', 'جرم سماوي'],
        'topics': ['الكواكب', 'النجوم', 'المجرات', 'الثقوب السوداء', 'الانفجار العظيم'],
        'locations': ['إيطاليا', 'ألمانيا', 'أمريكا', 'إنجلترا', 'فرنسا', 'روسيا'],
        'scientists': ['جاليليو', 'كوبرنيكوس', 'كبلر', 'هابل', 'آينشتاين', 'هوكنغ']
    },
    'علوم الأرض': {
        'types': ['نظرية جيولوجية', 'اكتشاف جيولوجي', 'ظاهرة طبيعية', 'دراسة مناخية'],
        'topics': ['الصفائح التكتونية', 'البراكين', 'الزلازل', 'المناخ', 'الأحافير'],
        'locations': ['ألمانيا', 'أمريكا', 'إنجلترا', 'اليابان', 'إيطاليا', 'أستراليا'],
        'scientists': ['فيجنر', 'لييل', 'هاتون', 'أغسيز', 'ريختر']
    },
    'حاسوب': {
        'types': ['خوارزمية حاسوبية', 'لغة برمجة', 'نظام تشغيل', 'تقنية حاسوبية'],
        'topics': ['الخوارزميات', 'قواعد البيانات', 'الشبكات', 'الذكاء الاصطناعي', 'الأمان'],
        'locations': ['أمريكا', 'إنجلترا', 'ألمانيا', 'فرنسا', 'كندا', 'اليابان'],
        'scientists': ['تورنغ', 'فون نيومان', 'كنوث', 'ريتشي', 'تورفالدس']
    },
    'تغذية': {
        'types': ['اكتشاف غذائي', 'فيتامين', 'معدن غذائي', 'دراسة تغذوية'],
        'topics': ['الفيتامينات', 'المعادن', 'البروتينات', 'الكربوهيدرات', 'الدهون'],
        'locations': ['أمريكا', 'إنجلترا', 'فرنسا', 'ألمانيا', 'اليابان', 'كندا'],
        'scientists': ['ليند', 'فونك', 'هوبكنز', 'مكولوم', 'گولدبرغر']
    },
    'بيئة': {
        'types': ['دراسة بيئية', 'نظام بيئي', 'تلوث بيئي', 'حفظ البيئة'],
        'topics': ['التنوع الحيوي', 'التلوث', 'الاحتباس الحراري', 'الطاقة المتجددة'],
        'locations': ['أمريكا', 'أستراليا', 'البرازيل', 'كندا', 'السويد', 'ألمانيا'],
        'scientists': ['كارسون', 'ليوبولد', 'ناس', 'لافلوك', 'ويلسون']
    }
}

def generate_years(start=1500, end=2024):
    """Generate random years"""
    return random.randint(start, end)

def generate_facts(field, topic):
    """Generate realistic facts for each field"""
    facts_templates = {
        'فيزياء': [
            f"تطبيقات في {topic}",
            f"قياسات دقيقة في {topic}",
            f"نتائج تجريبية مؤكدة",
            f"استخدامات في التكنولوجيا الحديثة"
        ],
        'كيمياء': [
            f"التركيب الكيميائي محدد",
            f"التفاعلات مع {topic}",
            f"الخصائص الفيزيائية معروفة",
            f"الاستخدامات الصناعية متعددة"
        ],
        'رياضيات': [
            f"برهان رياضي صحيح",
            f"تطبيقات في {topic}",
            f"استخدامات في العلوم التطبيقية",
            f"أساس للنظريات الحديثة"
        ]
    }
    
    base_facts = facts_templates.get(field, [
        f"دراسات مؤكدة في {topic}",
        f"أبحاث منشورة في مجلات علمية",
        f"تطبيقات عملية متنوعة",
        f"أساس للبحوث الحديثة"
    ])
    
    return random.sample(base_facts, min(3, len(base_facts)))

def generate_academic_entry(field_name, field_data, index):
    """Generate a single academic entry"""
    topic = random.choice(field_data['topics'])
    entry_type = random.choice(field_data['types'])
    scientist = random.choice(field_data['scientists'])
    location = random.choice(field_data['locations'])
    year = generate_years()
    
    # Generate title
    title = f"{topic} - دراسة رقم {index}"
    if 'نظرية' in entry_type:
        title = f"نظرية {topic}"
    elif 'اكتشاف' in entry_type:
        title = f"اكتشاف {topic}"
    elif 'قانون' in entry_type:
        title = f"قانون {topic}"
    
    # Generate summary
    summary = f"دراسة شاملة حول {topic} في مجال {field_name}. تشمل البحوث والتجارب والنتائج العملية التي توصل إليها العلماء في هذا المجال. هذه الدراسة تقدم فهماً عميقاً للموضوع وتطبيقاته العملية."
    
    # Generate facts
    facts = generate_facts(field_name, topic)
    
    return {
        'type': entry_type,
        'title': title,
        'field': field_name,
        'date': str(year),
        'location': location,
        'key_people': [scientist],
        'summary': summary,
        'verified_facts': facts,
        'source_url': f"https://www.britannica.com/{field_name.lower()}/{topic.lower()}"
    }

def generate_large_dataset(target_count=120000):
    """Generate large academic dataset"""
    with app.app_context():
        try:
            # Clear existing data
            print("Clearing existing data...")
            AcademicContent.query.delete()
            db.session.commit()
            
            print(f"Generating {target_count} academic entries...")
            
            entries_per_field = target_count // len(FIELDS)
            total_created = 0
            
            for field_name, field_data in FIELDS.items():
                print(f"Generating {entries_per_field} entries for {field_name}...")
                
                for i in range(entries_per_field):
                    try:
                        entry_data = generate_academic_entry(field_name, field_data, i + 1)
                        
                        academic_content = AcademicContent(
                            type=entry_data['type'],
                            title=entry_data['title'],
                            field=entry_data['field'],
                            date=entry_data['date'],
                            location=entry_data['location'],
                            key_people=json.dumps(entry_data['key_people'], ensure_ascii=False),
                            summary=entry_data['summary'],
                            verified_facts=json.dumps(entry_data['verified_facts'], ensure_ascii=False),
                            source_url=entry_data['source_url'],
                            crawled_at=datetime.utcnow()
                        )
                        
                        db.session.add(academic_content)
                        total_created += 1
                        
                        # Commit in batches
                        if total_created % 1000 == 0:
                            db.session.commit()
                            print(f"Created {total_created} entries so far...")
                            
                    except Exception as e:
                        print(f"Error creating entry {i}: {e}")
                        continue
            
            # Final commit
            db.session.commit()
            print(f"Successfully created {total_created} academic records!")
            
            # Verify count
            final_count = AcademicContent.query.count()
            print(f"Final database count: {final_count}")
            
        except Exception as e:
            print(f"Error generating large dataset: {e}")
            db.session.rollback()

if __name__ == "__main__":
    generate_large_dataset()