/**
 * Video Player Controller
 * Handles YouTube IFrame API integration
 */

class VideoPlayer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.player = null;
        this.videoId = null;
        this.isReady = false;
    }
    
    /**
     * Load and embed a YouTube video
     * @param {string} videoId - YouTube video ID
     */
    loadVideo(videoId) {
        this.videoId = videoId;
        
        // Create iframe element
        this.container.innerHTML = `
            <iframe 
                id="youtube-player"
                width="100%" 
                height="100%" 
                src="https://www.youtube.com/embed/${videoId}?enablejsapi=1&rel=0&modestbranding=1"
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen
                class="w-full h-full"
            ></iframe>
        `;
        
        // Initialize YouTube IFrame API
        this.initYouTubeAPI();
    }
    
    /**
     * Initialize YouTube IFrame API if not already loaded
     */
    initYouTubeAPI() {
        if (window.YT && window.YT.Player) {
            this.createPlayer();
            return;
        }
        
        // Load YouTube IFrame API
        const tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        
        // Wait for API to be ready
        window.onYouTubeIframeAPIReady = () => {
            this.createPlayer();
        };
    }
    
    /**
     * Create YouTube Player instance
     */
    createPlayer() {
        this.player = new YT.Player('youtube-player', {
            events: {
                'onReady': (event) => {
                    this.isReady = true;
                    this.player = event.target;
                },
                'onError': (event) => {
                    console.error('YouTube player error:', event.data);
                }
            }
        });
    }
    
    /**
     * Seek to specific time
     * @param {number} seconds - Time in seconds
     */
    seekTo(seconds) {
        if (this.player && this.isReady) {
            this.player.seekTo(seconds, true);
        }
    }
    
    /**
     * Pause playback
     */
    pause() {
        if (this.player && this.isReady) {
            this.player.pauseVideo();
        }
    }
    
    /**
     * Play video
     */
    play() {
        if (this.player && this.isReady) {
            this.player.playVideo();
        }
    }
    
    /**
     * Get current playback time
     * @returns {number} Current time in seconds
     */
    getCurrentTime() {
        if (this.player && this.isReady) {
            return Math.floor(this.player.getCurrentTime());
        }
        return 0;
    }
    
    /**
     * Get video duration
     * @returns {number} Duration in seconds
     */
    getDuration() {
        if (this.player && this.isReady) {
            return this.player.getDuration();
        }
        return 0;
    }
    
    /**
     * Destroy player instance
     */
    destroy() {
        if (this.player && this.isReady) {
            this.player.destroy();
        }
        this.container.innerHTML = '';
        this.player = null;
        this.isReady = false;
    }
}

// Export for use in other modules
window.VideoPlayer = VideoPlayer;