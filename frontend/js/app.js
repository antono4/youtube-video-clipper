/**
 * YouTube Video Clipper - Main Application Logic
 */

class YouTubeClipper {
    constructor() {
        // State
        this.api = new ClipperAPI();
        this.player = null;
        this.videoId = null;
        this.videoDuration = 0;
        this.startTime = 0;
        this.endTime = 30;
        this.currentSessionId = null;
        this.maxDuration = 300; // 5 minutes
        
        this.initElements();
        this.bindEvents();
    }
    
    initElements() {
        // URL Input elements
        this.urlInput = document.getElementById('videoUrl');
        this.validateBtn = document.getElementById('validateBtn');
        this.validationStatus = document.getElementById('validationStatus');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        
        // Preview elements
        this.previewSection = document.getElementById('previewSection');
        this.playerContainer = document.getElementById('playerContainer');
        this.videoTitle = document.getElementById('videoTitle');
        this.videoUploader = document.getElementById('videoUploader').querySelector('span');
        this.videoDurationEl = document.getElementById('videoDuration').querySelector('span');
        
        // Timeline elements
        this.startTimeInput = document.getElementById('startTime');
        this.endTimeInput = document.getElementById('endTime');
        this.startSlider = document.getElementById('startSlider');
        this.endSlider = document.getElementById('endSlider');
        this.clipDuration = document.getElementById('clipDuration');
        this.maxDurationWarning = document.getElementById('maxDurationWarning');
        
        // Process elements
        this.processBtn = document.getElementById('processBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercent = document.getElementById('progressPercent');
        this.progressMessage = document.getElementById('progressMessage');
        
        // Result elements
        this.resultSection = document.getElementById('resultSection');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.resultInfo = document.getElementById('resultInfo');
        this.resetBtn = document.getElementById('resetBtn');
        
        // Initialize video player
        this.player = new VideoPlayer('playerContainer');
    }
    
    bindEvents() {
        // URL validation
        this.validateBtn.addEventListener('click', () => this.validateURL());
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.validateURL();
        });
        
        // Timeline controls
        this.startSlider.addEventListener('input', () => this.handleSliderChange());
        this.endSlider.addEventListener('input', () => this.handleSliderChange());
        this.startTimeInput.addEventListener('change', (e) => this.handleTimeInput('start', e.target.value));
        this.endTimeInput.addEventListener('change', (e) => this.handleTimeInput('end', e.target.value));
        
        // Process clip
        this.processBtn.addEventListener('click', () => this.processClip());
        
        // Reset
        this.resetBtn.addEventListener('click', () => this.reset());
    }
    
    // ========== Status Management ==========
    
    showStatus(message, type = 'info') {
        this.validationStatus.classList.remove('hidden');
        
        const colorMap = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'info': 'bg-yellow-500'
        };
        
        this.statusDot.className = `w-2 h-2 rounded-full ${colorMap[type] || colorMap.info} animate-pulse`;
        this.statusText.textContent = message;
    }
    
    hideStatus() {
        this.validationStatus.classList.add('hidden');
    }
    
    // ========== URL Validation ==========
    
    async validateURL() {
        const url = this.urlInput.value.trim();
        
        if (!url) {
            this.showStatus('Masukkan URL YouTube terlebih dahulu', 'error');
            return;
        }
        
        this.validateBtn.disabled = true;
        this.showStatus('Memvalidasi URL...');
        
        try {
            const response = await this.api.validateURL(url);
            this.videoId = response.video_id;
            this.videoDuration = response.duration;
            
            // Update UI with video info
            this.videoTitle.textContent = response.title;
            this.videoUploader.textContent = response.uploader;
            this.videoDurationEl.textContent = this.formatTime(response.duration);
            
            // Initialize player
            this.player.loadVideo(response.video_id);
            
            // Show preview section
            this.previewSection.classList.remove('hidden');
            this.hideStatus();
            
            // Initialize sliders
            this.initSliders();
            
            // Scroll to preview
            setTimeout(() => {
                this.previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
            
        } catch (error) {
            this.showStatus(error.message || 'Gagal memvalidasi URL', 'error');
            this.previewSection.classList.add('hidden');
        } finally {
            this.validateBtn.disabled = false;
        }
    }
    
    initSliders() {
        const duration = Math.max(this.videoDuration, 60);
        
        this.startSlider.max = duration;
        this.endSlider.max = duration;
        this.startSlider.value = 0;
        this.endSlider.value = Math.min(30, duration);
        
        this.startTime = 0;
        this.endTime = Math.min(30, duration);
        
        this.updateTimeDisplays();
        this.updateSliderStyles();
    }
    
    updateSliderStyles() {
        const start = this.startTime;
        const end = this.endTime;
        const range = this.videoDuration;
        
        const startPercent = (start / range) * 100;
        const endPercent = (end / range) * 100;
        
        const gradient = `
            linear-gradient(to right,
                #374151 0%, 
                #374151 ${startPercent}%, 
                rgba(220, 38, 38, 0.5) ${startPercent}%, 
                rgba(220, 38, 38, 0.5) ${endPercent}%, 
                #374151 ${endPercent}%, 
                #374151 100%)
        `;
        
        this.startSlider.style.background = gradient;
    }
    
    // ========== Timeline Controls ==========
    
    handleSliderChange() {
        let start = parseInt(this.startSlider.value);
        let end = parseInt(this.endSlider.value);
        
        // Ensure start is less than end
        if (start >= end) {
            start = end - 1;
            this.startSlider.value = start;
        }
        if (end <= start) {
            end = start + 1;
            this.endSlider.value = end;
        }
        
        this.startTime = start;
        this.endTime = end;
        
        this.updateTimeDisplays();
        this.updateSliderStyles();
        
        // Sync player if needed
        // this.player.seekTo(start);
    }
    
    handleTimeInput(type, value) {
        const seconds = this.parseTime(value);
        
        if (seconds === null) {
            this.showStatus('Format waktu tidak valid. Gunakan format HH:MM:SS', 'error');
            return;
        }
        
        if (type === 'start') {
            if (seconds >= this.endTime) {
                this.showStatus('Waktu mulai harus lebih kecil dari waktu selesai', 'error');
                this.startTimeInput.value = this.formatTime(this.startTime);
                return;
            }
            this.startTime = seconds;
            this.startSlider.value = seconds;
        } else {
            if (seconds <= this.startTime) {
                this.showStatus('Waktu selesai harus lebih besar dari waktu mulai', 'error');
                this.endTimeInput.value = this.formatTime(this.endTime);
                return;
            }
            this.endTime = seconds;
            this.endSlider.value = seconds;
        }
        
        this.updateTimeDisplays();
        this.updateSliderStyles();
        this.hideStatus();
    }
    
    updateTimeDisplays() {
        this.startTimeInput.value = this.formatTime(this.startTime);
        this.endTimeInput.value = this.formatTime(this.endTime);
        
        const duration = this.endTime - this.startTime;
        this.clipDuration.innerHTML = `Durasi: <span class="text-white font-semibold">${this.formatDuration(duration)}</span>`;
        
        // Show warning if exceeds 5 minutes
        if (duration > this.maxDuration) {
            this.maxDurationWarning.classList.remove('hidden');
            this.processBtn.disabled = true;
        } else {
            this.maxDurationWarning.classList.add('hidden');
            this.processBtn.disabled = false;
        }
    }
    
    // ========== Clip Processing ==========
    
    async processClip() {
        const url = this.urlInput.value.trim();
        
        // Validate time range
        if (this.endTime <= this.startTime) {
            this.showStatus('Waktu selesai harus lebih besar dari waktu mulai', 'error');
            return;
        }
        
        // Show progress
        this.progressContainer.classList.remove('hidden');
        this.processBtn.disabled = true;
        this.resultSection.classList.add('hidden');
        
        // Reset progress
        this.updateProgress(0, 'Menghubungi server...');
        
        try {
            // Simulate initial progress
            this.simulateProgress(20, 'Memproses video...');
            
            const response = await this.api.processClip(url, this.startTime, this.endTime);
            
            if (response.success) {
                this.currentSessionId = response.session_id;
                this.updateProgress(100, 'Selesai!');
                
                // Update download button
                this.downloadBtn.href = response.file_path;
                this.downloadBtn.download = `clip_${this.formatTime(this.startTime).replace(/:/g, '-')}_${this.formatTime(this.endTime).replace(/:/g, '-')}.mp4`;
                this.resultInfo.textContent = `Clip ${this.formatTime(this.startTime)} - ${this.formatTime(this.endTime)} (${this.formatFileSize(response.file_size)})`;
                
                // Show result section
                setTimeout(() => {
                    this.progressContainer.classList.add('hidden');
                    this.resultSection.classList.remove('hidden');
                    this.resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 500);
            } else {
                throw new Error(response.message);
            }
            
        } catch (error) {
            this.showStatus(error.message || 'Gagal memproses video', 'error');
            this.progressContainer.classList.add('hidden');
        } finally {
            this.processBtn.disabled = false;
        }
    }
    
    simulateProgress(target, message) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 12;
            if (progress >= target) {
                progress = target;
                clearInterval(interval);
            }
            this.updateProgress(progress, message);
        }, 400);
        
        return interval;
    }
    
    updateProgress(percent, message) {
        this.progressBar.style.width = `${percent}%`;
        this.progressPercent.textContent = `${Math.round(percent)}%`;
        this.progressMessage.textContent = message;
    }
    
    // ========== Reset ==========
    
    reset() {
        // Clear result
        this.resultSection.classList.add('hidden');
        this.currentSessionId = null;
        
        // Reset time inputs
        this.startTime = 0;
        this.endTime = Math.min(30, this.videoDuration);
        this.updateTimeDisplays();
        this.initSliders();
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    // ========== Utility Functions ==========
    
    formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    
    parseTime(timeStr) {
        const parts = timeStr.split(':').map(Number);
        if (parts.some(isNaN)) return null;
        
        if (parts.length === 3) {
            return parts[0] * 3600 + parts[1] * 60 + parts[2];
        } else if (parts.length === 2) {
            return parts[0] * 60 + parts[1];
        } else if (parts.length === 1) {
            return parts[0];
        }
        return null;
    }
    
    formatDuration(seconds) {
        if (seconds < 60) return `${seconds} detik`;
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return s > 0 ? `${m} menit ${s} detik` : `${m} menit`;
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.clipper = new YouTubeClipper();
});