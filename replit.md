# Overview

This project is an Arabic Academic Content Crawler API that extracts educational and scientific content from reputable academic sources. The system crawls websites like Britannica, NASA, and other educational domains to collect structured academic information, processes it, and stores it in a database with Arabic field mappings. It provides a Flask-based web interface with real-time crawling status updates and data visualization.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework Architecture
The application uses Flask as the web framework with a traditional MVC pattern. The main application is structured with separate modules for routes, models, and business logic. Database operations are handled through SQLAlchemy ORM with a DeclarativeBase class structure.

## Database Design
The system uses SQLite as the default database (configurable via environment variables) with two main tables:
- **AcademicContent**: Stores extracted academic content with fields for type, title, field, date, location, key people, summary, verified facts, and source URL
- **CrawlStatus**: Tracks crawling operations with domain, timestamps, item counts, and error information

The database uses JSON columns for storing arrays (key_people, verified_facts) and includes automatic timestamp tracking for crawled content.

## Web Crawling Architecture
The crawler is built with a concurrent approach using ThreadPoolExecutor for parallel processing. It integrates multiple content extraction libraries:
- **trafilatura** for clean text extraction
- **BeautifulSoup** for HTML parsing and structured data extraction
- **requests** with session management for HTTP operations

The crawler implements rate limiting with configurable delays and includes user-agent rotation to avoid blocking.

## Content Processing Pipeline
A dedicated DataProcessor class handles the transformation and storage of crawled data. It includes:
- Duplicate detection based on title and field
- Batch processing for database operations (commits every 100 items)
- JSON serialization for complex data structures
- Error handling and logging for failed operations

## Frontend Architecture
The web interface uses Bootstrap RTL for Arabic language support with a responsive design. The frontend includes:
- Real-time status updates via AJAX polling
- Progress tracking for crawling operations
- Statistics dashboard with data visualization
- Sample data preview functionality

## Configuration Management
Academic sources are configured in a separate module with structured definitions for:
- Base URLs for different domains
- CSS selectors for content extraction
- Field mappings from English to Arabic
- Domain-specific crawling rules

## Background Task Processing
The system implements background crawling using Python threading with global status tracking. This allows for non-blocking crawling operations while providing real-time progress updates to the web interface.

# External Dependencies

## Web Crawling Libraries
- **trafilatura**: Primary library for extracting clean text content from web pages
- **BeautifulSoup**: HTML parsing and DOM manipulation for structured data extraction
- **requests**: HTTP client library with session management and connection pooling

## Web Framework Stack
- **Flask**: Core web framework for routing and request handling
- **SQLAlchemy**: ORM for database operations and model management
- **Werkzeug**: WSGI utilities including ProxyFix middleware for deployment

## Frontend Technologies
- **Bootstrap 5 RTL**: CSS framework with right-to-left language support
- **Font Awesome**: Icon library for user interface elements
- **JavaScript**: Client-side functionality for real-time updates and user interactions

## Target Academic Sources
- **Britannica.com**: Encyclopedia content across multiple scientific fields
- **NASA.gov**: Space and astronomy content from official NASA sources
- **Educational domains**: Various .edu and .org domains for academic content
- **Field-specific websites**: Sources categorized by academic disciplines (physics, chemistry, mathematics, biology, history, astronomy, geology, computer science)

## Database Options
- **SQLite**: Default local database for development and small deployments
- **PostgreSQL**: Configurable via DATABASE_URL environment variable for production use
- Connection pooling and health checks configured through SQLAlchemy engine options