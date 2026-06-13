/**
 * Timeline Controller
 * Custom dual-handle slider for selecting video segments
 */

class TimelineController {
    constructor(startSliderId, endSliderId, options = {}) {
        this.startSlider = document.getElementById(startSliderId);
        this.endSlider = document.getElementById(endSliderId);
        this.options = {
            min: 0,
            max: 100,
            step: 1,
            onChange: null,
            ...options
        };
        
        if (this.startSlider && this.endSlider) {
            this.init();
        }
    }
    
    init() {
        // Set initial attributes
        this.startSlider.min = this.options.min;
        this.startSlider.max = this.options.max;
        this.startSlider.step = this.options.step;
        
        this.endSlider.min = this.options.min;
        this.endSlider.max = this.options.max;
        this.endSlider.step = this.options.step;
        
        // Add event listeners
        this.startSlider.addEventListener('input', () => this.handleStartChange());
        this.endSlider.addEventListener('input', () => this.handleEndChange());
        
        // Initialize visual state
        this.updateSliderStyles();
    }
    
    handleStartChange() {
        let start = parseInt(this.startSlider.value);
        let end = parseInt(this.endSlider.value);
        
        // Ensure start is always less than end
        if (start >= end) {
            start = end - 1;
            this.startSlider.value = start;
        }
        
        this.updateSliderStyles();
        this.notifyChange('start', start, end);
    }
    
    handleEndChange() {
        let start = parseInt(this.startSlider.value);
        let end = parseInt(this.endSlider.value);
        
        // Ensure end is always greater than start
        if (end <= start) {
            end = start + 1;
            this.endSlider.value = end;
        }
        
        this.updateSliderStyles();
        this.notifyChange('end', start, end);
    }
    
    updateSliderStyles() {
        const start = parseInt(this.startSlider.value);
        const end = parseInt(this.endSlider.value);
        const range = this.options.max - this.options.min;
        
        const startPercent = ((start - this.options.min) / range) * 100;
        const endPercent = ((end - this.options.min) / range) * 100;
        
        // Create a visual gap between the two handles
        // This creates a "track" effect showing the selected range
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
        this.endSlider.style.background = 'transparent';
    }
    
    notifyChange(type, start, end) {
        if (this.options.onChange && typeof this.options.onChange === 'function') {
            this.options.onChange(type, start, end);
        }
    }
    
    /**
     * Set the range (min/max values)
     * @param {number} min - Minimum value
     * @param {number} max - Maximum value
     */
    setRange(min, max) {
        this.options.min = min;
        this.options.max = max;
        
        this.startSlider.min = min;
        this.startSlider.max = max;
        this.endSlider.min = min;
        this.endSlider.max = max;
        
        // Reset values to new range
        this.startSlider.value = min;
        this.endSlider.value = Math.min(min + 10, max);
        
        this.updateSliderStyles();
    }
    
    /**
     * Set slider values
     * @param {number} start - Start time value
     * @param {number} end - End time value
     */
    setValues(start, end) {
        this.startSlider.value = start;
        this.endSlider.value = end;
        this.updateSliderStyles();
    }
    
    /**
     * Get current slider values
     * @returns {Object} {start, end}
     */
    getValues() {
        return {
            start: parseInt(this.startSlider.value),
            end: parseInt(this.endSlider.value)
        };
    }
    
    /**
     * Disable/enable the sliders
     * @param {boolean} disabled - Whether to disable
     */
    setDisabled(disabled) {
        this.startSlider.disabled = disabled;
        this.endSlider.disabled = disabled;
    }
}

// Export for use in other modules
window.TimelineController = TimelineController;