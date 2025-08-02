#!/usr/bin/env python3
"""Create sample academic data for demonstration"""

import json
import logging
from app import app, db
from models import AcademicContent
from datetime import datetime

# Sample academic data in the exact format requested
sample_data = [
    {
        "type": "نظرية علمية",
        "title": "نظرية النسبية الخاصة",
        "field": "فيزياء",
        "date": "1905",
        "location": "ألمانيا",
        "key_people": ["ألبرت أينشتاين"],
        "summary": "نظرية تصف العلاقة بين الزمان والمكان وتوضح مفهوم تباطؤ الزمن والطاقة النسبية. تنص على أن سرعة الضوء ثابتة في جميع الأطر المرجعية.",
        "verified_facts": [
            "معادلة E=mc²",
            "نشرت في مجلة Annalen der Physik",
            "أساس لفيزياء الكم الحديثة"
        ],
        "source_url": "https://www.britannica.com/science/special-relativity"
    },
    {
        "type": "اكتشاف علمي",
        "title": "اكتشاف الحمض النووي DNA",
        "field": "أحياء",
        "date": "1953",
        "location": "إنجلترا",
        "key_people": ["جيمس واتسون", "فرانسيس كريك", "روزاليند فرانكلين"],
        "summary": "اكتشاف البنية المزدوجة الحلزونية للحمض النووي الذي يحمل المعلومات الوراثية في جميع الكائنات الحية.",
        "verified_facts": [
            "البنية المزدوجة الحلزونية",
            "نشر في مجلة Nature عام 1953",
            "حصل واتسون وكريك على جائزة نوبل عام 1962"
        ],
        "source_url": "https://www.britannica.com/science/DNA"
    },
    {
        "type": "نظرية رياضية",
        "title": "نظرية فيثاغورس",
        "field": "رياضيات",
        "date": "القرن السادس ق.م",
        "location": "اليونان القديمة",
        "key_people": ["فيثاغورس"],
        "summary": "في المثلث القائم الزاوية، مربع طول الوتر يساوي مجموع مربعي طولي الضلعين الآخرين.",
        "verified_facts": [
            "a² + b² = c²",
            "تطبق على جميع المثلثات قائمة الزاوية",
            "أساس في الهندسة الإقليدية"
        ],
        "source_url": "https://www.britannica.com/science/Pythagorean-theorem"
    },
    {
        "type": "تجربة علمية",
        "title": "تجربة مندل الوراثية",
        "field": "أحياء",
        "date": "1866",
        "location": "النمسا",
        "key_people": ["جريجور مندل"],
        "summary": "تجارب على نباتات البازلاء كشفت قوانين الوراثة الأساسية وكيفية انتقال الصفات من الآباء إلى الأبناء.",
        "verified_facts": [
            "قانون الفصل المندلي",
            "قانون التوزيع المستقل",
            "أسس علم الوراثة الحديث"
        ],
        "source_url": "https://www.britannica.com/biography/Gregor-Mendel"
    },
    {
        "type": "اكتشاف كيميائي",
        "title": "الجدول الدوري للعناصر",
        "field": "كيمياء",
        "date": "1869",
        "location": "روسيا",
        "key_people": ["ديمتري مندليف"],
        "summary": "ترتيب العناصر الكيميائية حسب العدد الذري والخصائص الدورية، مما يكشف عن نمط دوري في خصائص العناصر.",
        "verified_facts": [
            "118 عنصر معروف حالياً",
            "ترتيب حسب العدد الذري",
            "التنبؤ بخصائص العناصر غير المكتشفة"
        ],
        "source_url": "https://www.britannica.com/science/periodic-table"
    },
    {
        "type": "نظرية فلكية",
        "title": "نظرية الانفجار العظيم",
        "field": "فلك",
        "date": "1927",
        "location": "بلجيكا",
        "key_people": ["جورج لومتر", "إدوين هابل"],
        "summary": "نظرية تفسر نشأة الكون من نقطة واحدة شديدة الكثافة والحرارة قبل 13.8 مليار سنة.",
        "verified_facts": [
            "عمر الكون 13.8 مليار سنة",
            "الكون يتمدد باستمرار",
            "إشعاع الخلفية الكونية الميكروي"
        ],
        "source_url": "https://www.britannica.com/science/big-bang-model"
    },
    {
        "type": "اكتشاف تاريخي",
        "title": "حجر رشيد",
        "field": "تاريخ",
        "date": "1799",
        "location": "مصر",
        "key_people": ["جان فرانسوا شامبليون"],
        "summary": "حجر يحمل نصاً واحداً بثلاث لغات مختلفة، مما مكن من فك رموز الهيروغليفية المصرية القديمة.",
        "verified_facts": [
            "مكتوب بالهيروغليفية والديموطيقية واليونانية",
            "فك شامبليون رموز الهيروغليفية عام 1822",
            "محفوظ في المتحف البريطاني"
        ],
        "source_url": "https://www.britannica.com/topic/Rosetta-Stone"
    },
    {
        "type": "نظرية علوم أرض",
        "title": "نظرية الصفائح التكتونية",
        "field": "علوم الأرض",
        "date": "1960s",
        "location": "دولي",
        "key_people": ["ألفريد فيجنر", "هاري هيس"],
        "summary": "نظرية تفسر حركة القارات والصفائح الأرضية وتكوين الجبال والزلازل والبراكين.",
        "verified_facts": [
            "القارات تتحرك بسرعة بضعة سنتيمترات سنوياً",
            "حدود الصفائح مواقع النشاط الزلزالي",
            "تفسر توزيع الأحافير والصخور"
        ],
        "source_url": "https://www.britannica.com/science/plate-tectonics"
    },
    {
        "type": "معلومة حاسوب",
        "title": "خوارزمية الترتيب السريع",
        "field": "حاسوب",
        "date": "1960",
        "location": "إنجلترا",
        "key_people": ["توني هور"],
        "summary": "خوارزمية فعالة لترتيب قوائم البيانات باستخدام مبدأ 'فرّق تسد' مع متوسط تعقيد زمني O(n log n).",
        "verified_facts": [
            "متوسط التعقيد الزمني O(n log n)",
            "أسوأ حالة O(n²)",
            "واحدة من أكثر خوارزميات الترتيب استخداماً"
        ],
        "source_url": "https://www.britannica.com/technology/quicksort"
    },
    {
        "type": "معلومة تغذية",
        "title": "فيتامين C وعلاج الإسقربوط",
        "field": "تغذية",
        "date": "1747",
        "location": "اسكتلندا",
        "key_people": ["جيمس ليند"],
        "summary": "اكتشاف أن فيتامين C الموجود في الحمضيات يمنع ويعالج مرض الإسقربوط، أول تجربة إكلينيكية مضبوطة.",
        "verified_facts": [
            "أول تجربة إكلينيكية مضبوطة في التاريخ",
            "الجرعة اليومية الموصى بها 90 ملغ للرجال",
            "ضروري لتكوين الكولاجين"
        ],
        "source_url": "https://www.britannica.com/science/vitamin-C"
    }
]

def create_sample_data():
    """Create sample academic data in the database"""
    with app.app_context():
        try:
            # Clear existing data
            AcademicContent.query.delete()
            
            # Add sample data
            for item in sample_data:
                academic_content = AcademicContent(
                    type=item['type'],
                    title=item['title'],
                    field=item['field'],
                    date=item['date'],
                    location=item['location'],
                    key_people=json.dumps(item['key_people'], ensure_ascii=False),
                    summary=item['summary'],
                    verified_facts=json.dumps(item['verified_facts'], ensure_ascii=False),
                    source_url=item['source_url'],
                    crawled_at=datetime.utcnow()
                )
                db.session.add(academic_content)
            
            db.session.commit()
            print(f"Successfully created {len(sample_data)} sample academic records")
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_sample_data()