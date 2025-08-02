// Arabic Academic Crawler Frontend JavaScript

class AcademicCrawlerApp {
    constructor() {
        this.isPolling = false;
        this.pollingInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateUI();
        // Remove status polling since we're showing static data
    }

    bindEvents() {
        // Start crawling button
        document.getElementById('startCrawling').addEventListener('click', () => {
            this.startCrawling();
        });

        // Stop crawling button
        document.getElementById('stopCrawling').addEventListener('click', () => {
            this.stopCrawling();
        });

        // Refresh sample data
        window.refreshSample = () => {
            this.refreshSampleData();
        };
    }

    async startCrawling() {
        const targetCount = document.getElementById('targetCount').value || 290000;
        const startBtn = document.getElementById('startCrawling');
        const stopBtn = document.getElementById('stopCrawling');

        try {
            startBtn.disabled = true;
            startBtn.innerHTML = '<span class="loading me-2"></span>جاري البدء...';

            const response = await fetch('/start_crawling', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    target_count: parseInt(targetCount)
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('تم بدء عملية الزحف بنجاح!', 'success');
                stopBtn.disabled = false;
                this.startStatusPolling();
            } else {
                throw new Error(result.error || 'خطأ غير معروف');
            }

        } catch (error) {
            this.showNotification(`خطأ: ${error.message}`, 'error');
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play me-2"></i>بدء عملية الزحف';
        }
    }

    stopCrawling() {
        const startBtn = document.getElementById('startCrawling');
        const stopBtn = document.getElementById('stopCrawling');
        
        // Reset UI
        startBtn.disabled = false;
        startBtn.innerHTML = '<i class="fas fa-play me-2"></i>بدء عملية الزحف';
        stopBtn.disabled = true;
        
        this.stopStatusPolling();
        this.showNotification('تم إيقاف عملية الزحف', 'warning');
    }

    async startStatusPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        this.pollingInterval = setInterval(async () => {
            try {
                const response = await fetch('/crawling_status');
                const status = await response.json();
                this.updateCrawlingStatus(status);

                // Stop polling if crawling is complete
                if (!status.is_running) {
                    this.stopStatusPolling();
                    this.updateUI();
                }
            } catch (error) {
                console.error('Error polling status:', error);
            }
        }, 2000); // Poll every 2 seconds
    }

    stopStatusPolling() {
        this.isPolling = false;
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    updateCrawlingStatus(status) {
        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        const crawlProgress = document.getElementById('crawl-progress');
        const crawlStatus = document.getElementById('crawl-status');

        if (progressBar) {
            progressBar.style.width = `${status.progress}%`;
            progressBar.textContent = `${status.progress}%`;
            
            // Add animation classes based on status
            if (status.is_running) {
                progressBar.classList.add('progress-bar-striped', 'progress-bar-animated');
            } else {
                progressBar.classList.remove('progress-bar-striped', 'progress-bar-animated');
            }
        }

        if (crawlProgress) {
            crawlProgress.textContent = `${status.progress}%`;
        }

        if (crawlStatus) {
            crawlStatus.textContent = status.message;
            
            // Update badge class based on status
            crawlStatus.className = 'badge';
            if (status.is_running) {
                crawlStatus.classList.add('bg-warning', 'status-running');
            } else if (status.progress === 100) {
                crawlStatus.classList.add('bg-success', 'status-completed');
            } else {
                crawlStatus.classList.add('bg-secondary');
            }
        }

        // Update buttons
        const startBtn = document.getElementById('startCrawling');
        const stopBtn = document.getElementById('stopCrawling');

        if (status.is_running) {
            startBtn.disabled = true;
            startBtn.innerHTML = '<span class="loading me-2"></span>جاري الزحف...';
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play me-2"></i>بدء عملية الزحف';
            stopBtn.disabled = true;
        }
    }

    async refreshSampleData() {
        try {
            const response = await fetch('/api/data/sample?limit=5');
            const sampleData = await response.json();
            
            const sampleContainer = document.getElementById('sample-data');
            if (sampleContainer && sampleData.length > 0) {
                const formattedData = JSON.stringify(sampleData, null, 2);
                sampleContainer.innerHTML = `<pre class="bg-dark text-light p-3 rounded" style="max-height: 400px; overflow-y: auto;"><code>${this.highlightJSON(formattedData)}</code></pre>`;
            }
            
            this.showNotification('تم تحديث عينة البيانات', 'success');
        } catch (error) {
            this.showNotification('خطأ في تحديث البيانات', 'error');
        }
    }

    async updateUI() {
        try {
            // Update statistics
            const statsResponse = await fetch('/api/statistics');
            const stats = await statsResponse.json();
            
            // Update total items count
            const totalElements = document.querySelectorAll('.card-title');
            if (totalElements.length > 0) {
                totalElements[0].textContent = stats.total_items || 0;
            }
            
        } catch (error) {
            console.error('Error updating UI:', error);
        }
    }

    highlightJSON(json) {
        // Simple JSON syntax highlighting
        return json
            .replace(/("([^"\\]|\\.)*")\s*:/g, '<span class="json-key">$1</span>:')
            .replace(/:\s*("([^"\\]|\\.)*")/g, ': <span class="json-string">$1</span>')
            .replace(/:\s*(\d+)/g, ': <span class="json-number">$1</span>')
            .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; left: 20px; z-index: 9999; min-width: 300px;';
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-triangle' : 
                    type === 'warning' ? 'exclamation-circle' : 'info-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Format numbers with Arabic separators
    formatNumber(num) {
        return new Intl.NumberFormat('ar-EG').format(num);
    }

    // Utility method to copy JSON to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('تم نسخ البيانات إلى الحافظة', 'success');
        }).catch(() => {
            this.showNotification('خطأ في نسخ البيانات', 'error');
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.crawlerApp = new AcademicCrawlerApp();
});

// Add custom filter for JSON pretty printing in template
if (typeof window !== 'undefined') {
    window.tojsonpretty = function(obj) {
        return JSON.stringify(obj, null, 2);
    };
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add copy buttons to code blocks
document.addEventListener('DOMContentLoaded', () => {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-light position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.style.fontSize = '0.8rem';
        
        block.parentElement.style.position = 'relative';
        block.parentElement.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent);
            copyBtn.innerHTML = '<i class="fas fa-check text-success"></i>';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    });
});
