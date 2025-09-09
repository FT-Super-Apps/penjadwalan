// Enhanced University Scheduling System - Frontend JavaScript
// Handles file uploads, configuration, and scheduling visualization

class SchedulingInterface {
    constructor() {
        this.uploadedFiles = {
            courses: null,
            times: null,
            rooms: null,
            preferences: null
        };
        
        this.config = {
            algorithm: {},
            preferences: {},
            constraints: {}
        };
        
        this.currentResults = null;
        this.websocket = null;
        
        this.initializeEventListeners();
        this.initializeAnimations();
    }

    initializeEventListeners() {
        // File upload handlers
        this.setupFileUpload('courseFile', 'courseUploadZone', 'courseFileInfo', 'courseFileName', 'courses');
        this.setupFileUpload('timeFile', 'timeUploadZone', 'timeFileInfo', 'timeFileName', 'times');
        this.setupFileUpload('roomFile', 'roomUploadZone', 'roomFileInfo', 'roomFileName', 'rooms');
        this.setupFileUpload('prefFile', 'prefUploadZone', 'prefFileInfo', 'prefFileName', 'preferences');
        
        // Configuration listeners
        this.setupConfigurationListeners();
        
        // Scroll animations
        window.addEventListener('scroll', () => this.handleScrollAnimations());
    }

    setupFileUpload(inputId, zoneId, infoId, nameId, type) {
        const fileInput = document.getElementById(inputId);
        const uploadZone = document.getElementById(zoneId);
        const fileInfo = document.getElementById(infoId);
        const fileName = document.getElementById(nameId);

        // Click handler
        uploadZone.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                fileInput.click();
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileUpload(file, type, fileInfo, fileName);
            }
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && this.validateFileType(file)) {
                this.handleFileUpload(file, type, fileInfo, fileName);
                fileInput.files = e.dataTransfer.files;
            }
        });
    }

    validateFileType(file) {
        const validTypes = ['.csv', '.xlsx', '.xls'];
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        return validTypes.includes(fileExtension);
    }

    handleFileUpload(file, type, fileInfoElement, fileNameElement) {
        if (!this.validateFileType(file)) {
            this.showNotification('Invalid file type. Please upload CSV or Excel files.', 'error');
            return;
        }

        // Store file reference
        this.uploadedFiles[type] = file;
        
        // Update UI
        fileNameElement.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
        fileInfoElement.style.display = 'block';
        
        // Add animation
        fileInfoElement.classList.add('animate__animated', 'animate__fadeInUp');
        
        this.showNotification(`${type} file uploaded successfully!`, 'success');
        this.updateProcessButtonState();
        
        // Preview file data
        this.previewFileData(file, type);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    previewFileData(file, type) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                let data;
                if (file.name.endsWith('.csv')) {
                    data = this.parseCSV(e.target.result);
                } else {
                    // For Excel files, we'll handle this on the backend
                    console.log('Excel file uploaded, will be processed on server');
                    return;
                }
                
                this.validateDataStructure(data, type);
            } catch (error) {
                this.showNotification(`Error reading ${type} file: ${error.message}`, 'error');
            }
        };
        reader.readAsText(file);
    }

    parseCSV(csvText) {
        const lines = csvText.trim().split('\\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index];
            });
            data.push(row);
        }
        
        return { headers, data };
    }

    validateDataStructure(parsedData, type) {
        const requiredColumns = {
            courses: ['nama', 'dosen', 'sks'],
            times: ['hari', 'jam_mulai'],
            rooms: ['nama', 'kapasitas'],
            preferences: ['dosen'] // Optional file
        };

        const required = requiredColumns[type];
        if (!required) return true;

        const missing = required.filter(col => !parsedData.headers.includes(col));
        
        if (missing.length > 0 && type !== 'preferences') {
            this.showNotification(`Missing required columns in ${type}: ${missing.join(', ')}`, 'warning');
            return false;
        }

        this.showNotification(`${type} data structure validated successfully!`, 'success');
        return true;
    }

    removeFile(type) {
        this.uploadedFiles[type] = null;
        const fileInfo = document.getElementById(`${type}FileInfo`);
        const fileInput = document.getElementById(`${type}File`);
        
        fileInfo.style.display = 'none';
        fileInput.value = '';
        
        this.updateProcessButtonState();
        this.showNotification(`${type} file removed`, 'info');
    }

    setupConfigurationListeners() {
        // Algorithm configuration
        const algorithmInputs = ['populationSize', 'maxGenerations', 'crossoverRate', 'mutationRate', 'earlyTermination', 'minutesPerSks'];
        algorithmInputs.forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.updateConfiguration());
        });

        // Preferences configuration  
        const preferenceInputs = ['reservedPenalty', 'preferredPenalty', 'blockedPenalty', 'enableEnhanced'];
        preferenceInputs.forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.updateConfiguration());
        });

        // Constraints configuration
        const constraintInputs = ['clashWeight', 'allowPartial', 'optimizeFor'];
        constraintInputs.forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.updateConfiguration());
        });
    }

    updateConfiguration() {
        this.config = {
            algorithm: {
                populationSize: parseInt(document.getElementById('populationSize').value),
                maxGenerations: parseInt(document.getElementById('maxGenerations').value),
                crossoverRate: parseInt(document.getElementById('crossoverRate').value),
                mutationRate: parseInt(document.getElementById('mutationRate').value),
                earlyTermination: parseFloat(document.getElementById('earlyTermination').value),
                minutesPerSks: parseInt(document.getElementById('minutesPerSks').value)
            },
            preferences: {
                reservedPenalty: parseInt(document.getElementById('reservedPenalty').value),
                preferredPenalty: parseInt(document.getElementById('preferredPenalty').value),
                blockedPenalty: parseInt(document.getElementById('blockedPenalty').value),
                enableEnhanced: document.getElementById('enableEnhanced').checked
            },
            constraints: {
                clashWeight: parseInt(document.getElementById('clashWeight').value),
                allowPartial: document.getElementById('allowPartial').checked,
                optimizeFor: document.getElementById('optimizeFor').value
            }
        };
    }

    updateProcessButtonState() {
        const processBtn = document.getElementById('processBtn');
        const requiredFiles = ['courses', 'times', 'rooms'];
        const hasRequiredFiles = requiredFiles.every(type => this.uploadedFiles[type] !== null);
        
        processBtn.disabled = !hasRequiredFiles;
        
        if (hasRequiredFiles) {
            processBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Scheduling Optimization';
            processBtn.classList.remove('btn-secondary');
            processBtn.classList.add('process-btn');
        } else {
            processBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload Required Files First';
            processBtn.classList.add('btn-secondary');
        }
    }

    async startScheduling() {
        if (!this.validateInputs()) {
            return;
        }

        this.showLoadingSection();
        this.updateConfiguration();

        try {
            const formData = new FormData();
            
            // Add files
            Object.entries(this.uploadedFiles).forEach(([key, file]) => {
                if (file) {
                    formData.append(key, file);
                }
            });
            
            // Add configuration
            formData.append('config', JSON.stringify(this.config));
            
            // Start scheduling process
            const response = await fetch('/api/schedule', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle streaming response if WebSocket is available
            if (response.headers.get('content-type')?.includes('application/json')) {
                const result = await response.json();
                this.handleSchedulingComplete(result);
            } else {
                // Handle streaming response
                this.handleStreamingResponse(response);
            }

        } catch (error) {
            console.error('Scheduling error:', error);
            this.showNotification(`Scheduling failed: ${error.message}`, 'error');
            this.hideLoadingSection();
        }
    }

    validateInputs() {
        const requiredFiles = ['courses', 'times', 'rooms'];
        const missingFiles = requiredFiles.filter(type => !this.uploadedFiles[type]);
        
        if (missingFiles.length > 0) {
            this.showNotification(`Missing required files: ${missingFiles.join(', ')}`, 'error');
            return false;
        }

        // Validate configuration values
        if (this.config.algorithm.populationSize < 4) {
            this.showNotification('Population size must be at least 4', 'error');
            return false;
        }

        if (this.config.algorithm.crossoverRate < 50 || this.config.algorithm.crossoverRate > 95) {
            this.showNotification('Crossover rate should be between 50-95%', 'warning');
        }

        return true;
    }

    async handleStreamingResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            this.handleProgressUpdate(data);
                        } catch (e) {
                            console.log('Non-JSON data:', line);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Streaming error:', error);
            this.showNotification('Connection error during processing', 'error');
        }
    }

    handleProgressUpdate(data) {
        if (data.type === 'progress') {
            this.updateProgress(data.progress, data.message);
        } else if (data.type === 'generation') {
            this.updateProgress(data.generation / this.config.algorithm.maxGenerations * 100, 
                              `Generation ${data.generation}: Best fitness ${data.fitness.toFixed(4)}`);
        } else if (data.type === 'complete') {
            this.handleSchedulingComplete(data.result);
        } else if (data.type === 'error') {
            this.showNotification(data.message, 'error');
            this.hideLoadingSection();
        }
    }

    updateProgress(percentage, message) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = message;
    }

    handleSchedulingComplete(result) {
        this.currentResults = result;
        this.hideLoadingSection();
        this.showResults(result);
        this.showNotification('Scheduling optimization completed!', 'success');
    }

    showLoadingSection() {
        document.getElementById('loadingSection').style.display = 'block';
        document.getElementById('processBtn').disabled = true;
        
        // Scroll to loading section
        document.getElementById('loadingSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }

    hideLoadingSection() {
        document.getElementById('loadingSection').style.display = 'none';
        document.getElementById('processBtn').disabled = false;
        this.updateProgress(0, 'Ready to start');
    }

    showResults(result) {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        
        // Populate statistics
        this.populateStatistics(result.statistics);
        
        // Populate schedule table
        this.populateScheduleTable(result.schedule);
        
        // Add animations
        resultsSection.classList.add('animate__animated', 'animate__fadeInUp');
        
        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 500);
    }

    populateStatistics(stats) {
        const statsGrid = document.getElementById('statsGrid');
        
        const statisticsData = [
            {
                icon: 'fas fa-trophy',
                value: stats.fitness.toFixed(4),
                label: 'Best Fitness',
                color: 'text-success',
                bgColor: 'rgba(16, 185, 129, 0.1)'
            },
            {
                icon: 'fas fa-clock',
                value: `${stats.executionTime.toFixed(2)}s`,
                label: 'Execution Time',
                color: 'text-primary',
                bgColor: 'rgba(102, 126, 234, 0.1)'
            },
            {
                icon: 'fas fa-dna',
                value: stats.generations,
                label: 'Generations',
                color: 'text-info',
                bgColor: 'rgba(6, 182, 212, 0.1)'
            },
            {
                icon: 'fas fa-exclamation-triangle',
                value: stats.totalViolations,
                label: 'Total Violations',
                color: stats.totalViolations > 0 ? 'text-warning' : 'text-success',
                bgColor: stats.totalViolations > 0 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)'
            },
            {
                icon: 'fas fa-lock',
                value: stats.reservedViolations,
                label: 'Reserved Violations',
                color: stats.reservedViolations > 0 ? 'text-danger' : 'text-success',
                bgColor: stats.reservedViolations > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)'
            },
            {
                icon: 'fas fa-memory',
                value: `${stats.ramUsage}MB`,
                label: 'RAM Usage',
                color: 'text-secondary',
                bgColor: 'rgba(107, 114, 128, 0.1)'
            }
        ];

        statsGrid.innerHTML = statisticsData.map(stat => `
            <div class="stat-card" style="background: ${stat.bgColor};">
                <div class="stat-icon ${stat.color}">
                    <i class="${stat.icon}"></i>
                </div>
                <div class="stat-value ${stat.color}">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            </div>
        `).join('');
    }

    populateScheduleTable(schedule) {
        const scheduleBody = document.getElementById('scheduleBody');
        
        scheduleBody.innerHTML = schedule.map(item => {
            const statusClass = this.getStatusClass(item.status);
            const statusIcon = this.getStatusIcon(item.status);
            
            return `
                <tr>
                    <td><strong>${item.course}</strong></td>
                    <td>${item.lecturer}</td>
                    <td>${item.day}</td>
                    <td>${item.time}</td>
                    <td>${item.room}</td>
                    <td>
                        <span class="status-badge ${statusClass}">
                            <i class="${statusIcon} me-1"></i>
                            ${item.status}
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'ok':
            case 'optimal':
                return 'status-ok';
            case 'warning':
            case 'preference issue':
                return 'status-warning';
            case 'conflict':
            case 'clash':
            case 'reserved violation':
                return 'status-error';
            default:
                return 'status-ok';
        }
    }

    getStatusIcon(status) {
        switch (status.toLowerCase()) {
            case 'ok':
            case 'optimal':
                return 'fas fa-check-circle';
            case 'warning':
            case 'preference issue':
                return 'fas fa-exclamation-triangle';
            case 'conflict':
            case 'clash':
            case 'reserved violation':
                return 'fas fa-times-circle';
            default:
                return 'fas fa-info-circle';
        }
    }

    async exportSchedule(format) {
        if (!this.currentResults) {
            this.showNotification('No schedule data to export', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentResults)
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }

            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `schedule.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showNotification(`Schedule exported as ${format.toUpperCase()}`, 'success');

        } catch (error) {
            console.error('Export error:', error);
            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    async generateReport() {
        if (!this.currentResults) {
            this.showNotification('No data available for report generation', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    results: this.currentResults,
                    config: this.config
                })
            });

            if (!response.ok) {
                throw new Error(`Report generation failed: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'scheduling-report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showNotification('Detailed report generated successfully!', 'success');

        } catch (error) {
            console.error('Report generation error:', error);
            this.showNotification(`Report generation failed: ${error.message}`, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        const icon = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        }[type] || 'fas fa-info-circle';
        
        notification.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    initializeAnimations() {
        // Scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    handleScrollAnimations() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('visible');
            }
        });
    }
}

// Tab switching function
function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.config-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.config-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    event.target.classList.add('active');
    document.getElementById(`${tabName}-config`).classList.add('active');
}

// File removal functions
function removeCourseFile() {
    schedulingInterface.removeFile('course');
}

function removeTimeFile() {
    schedulingInterface.removeFile('time');
}

function removeRoomFile() {
    schedulingInterface.removeFile('room');
}

function removePrefFile() {
    schedulingInterface.removeFile('pref');
}

// Main functions
function startScheduling() {
    schedulingInterface.startScheduling();
}

function exportSchedule(format) {
    schedulingInterface.exportSchedule(format);
}

function generateReport() {
    schedulingInterface.generateReport();
}

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.schedulingInterface = new SchedulingInterface();
    
    // Add some demo functionality for development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('🎓 Enhanced Scheduling System - Development Mode');
        console.log('Available methods:', Object.getOwnPropertyNames(SchedulingInterface.prototype));
    }
});