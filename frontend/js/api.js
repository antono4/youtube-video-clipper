/**
 * API Communication Layer
 */

class ClipperAPI {
    constructor(baseURL = '') {
        // Default to localhost:8000 for development
        // In production, this should be the same domain or configured properly
        this.baseURL = baseURL || this.getBaseURL();
    }
    
    getBaseURL() {
        // Try to detect the API URL based on current location
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const port = window.location.port;
        
        // If running on the same host with different port (dev mode)
        if (port === '3000' || port === '80' || port === '') {
            // Backend typically runs on 8000 in dev
            return `${protocol}//${host}:8000`;
        }
        
        // Use same host (production mode with reverse proxy)
        return `${protocol}//${host}${port ? ':' + port : ''}`;
    }
    
    async validateURL(url) {
        const response = await fetch(`${this.baseURL}/api/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Validasi gagal');
        }
        
        return response.json();
    }
    
    async processClip(url, startTime, endTime) {
        const response = await fetch(`${this.baseURL}/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                start_time: startTime,
                end_time: endTime
            }),
        });
        
        return response.json();
    }
    
    async cleanupSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/cleanup/${sessionId}`, {
                method: 'DELETE',
            });
            return response.json();
        } catch (error) {
            console.warn('Cleanup failed:', error);
        }
    }
}

// Export for use in other modules
window.ClipperAPI = ClipperAPI;