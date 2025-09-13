// Application data
const danceStyles = [
    {"category": "Indian Classical", "styles": ["Bharatanatyam", "Kathak", "Kuchipudi", "Odissi", "Manipuri", "Mohiniyattam", "Kathakali", "Sattriya"]},
    {"category": "Western", "styles": ["Ballet", "Contemporary", "Jazz", "Tap Dancing", "Hip-Hop", "Breakdancing", "Popping", "Locking", "House Dance"]},
    {"category": "Latin", "styles": ["Salsa", "Bachata", "Merengue", "Rumba", "Cha-cha-cha", "Samba", "Argentine Tango", "Paso Doble"]},
    {"category": "Ballroom", "styles": ["Waltz", "Foxtrot", "Quickstep", "Viennese Waltz", "Tango", "Slow Foxtrot"]},
    {"category": "Folk & Traditional", "styles": ["Bhangra", "Garba", "Kalbelia", "Flamenco", "Irish Step Dancing", "Morris Dancing", "Cossack Dance", "Belly Dance"]},
    {"category": "Modern & Street", "styles": ["Krump", "Waacking", "Voguing", "Afrobeats", "K-Pop Choreography", "Commercial Dance", "Urban Dance"]},
    {"category": "Cultural", "styles": ["Bollywood", "Chinese Classical", "Japanese Butoh", "African Traditional", "Middle Eastern", "Polynesian", "Native American"]}
];

const themes = [
    {"name": "Dark", "primary": "#1a1a2e", "secondary": "#16213e", "accent": "#7f5af0"},
    {"name": "Light", "primary": "#ffffff", "secondary": "#f8fafc", "accent": "#6366f1"},
    {"name": "Auto", "primary": "auto", "secondary": "auto", "accent": "#7f5af0"}
];

const colorSchemes = [
    {"name": "Cosmic Purple", "primary": "#1a0933", "secondary": "#2d1b69", "accent": "#8b5cf6"},
    {"name": "Ocean Blue", "primary": "#0c4a6e", "secondary": "#0e7490", "accent": "#06b6d4"},
    {"name": "Forest Green", "primary": "#064e3b", "secondary": "#065f46", "accent": "#10b981"},
    {"name": "Sunset Orange", "primary": "#9a3412", "secondary": "#c2410c", "accent": "#f97316"},
    {"name": "Rose Pink", "primary": "#831843", "secondary": "#be185d", "accent": "#ec4899"},
    {"name": "Midnight Blue", "primary": "#1e1b4b", "secondary": "#312e81", "accent": "#6366f1"},
    {"name": "Emerald Mint", "primary": "#134e4a", "secondary": "#0f766e", "accent": "#14b8a6"},
    {"name": "Golden Amber", "primary": "#92400e", "secondary": "#d97706", "accent": "#f59e0b"},
    {"name": "Cherry Blossom", "primary": "#701a75", "secondary": "#a21caf", "accent": "#d946ef"},
    {"name": "Arctic Frost", "primary": "#1e293b", "secondary": "#334155", "accent": "#64748b"}
];

const animationOptions = [
    {"name": "Full Animations", "value": "full"},
    {"name": "Reduced Motion", "value": "reduced"},
    {"name": "Essential Only", "value": "essential"}
];

const qualityOptions = [
    {"name": "HD (1080p)", "value": "1080p"},
    {"name": "Standard (720p)", "value": "720p"},
    {"name": "Mobile (480p)", "value": "480p"}
];

// Application state
class DanceAIApp {
    constructor() {
        this.currentTheme = 'Dark';
        this.currentColorScheme = 'Cosmic Purple';
        this.animationPreference = 'full';
        this.videoQuality = '720p';
        this.animationsEnabled = true;
        this.history = [];
        this.isGenerating = false;
        this.heightUnit = 'cm';
        this.audioElement = null;
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 0;
        this.volume = 0.7;
        this.bpm = 0;
        this.genre = 'Detecting...';
        this.isHistoryCollapsed = window.innerWidth <= 768; // Start collapsed on mobile
        this.settingsCache = {};
        this.historyCache = [];
        
        this.init();
    }

    init() {
        try {
            this.loadSettings();
            this.showApp();
            // Delay setup to ensure DOM is fully ready
            setTimeout(() => {
                this.setupEventListeners();
                this.populateDanceStyles();
                this.populateSettingsOptions();
                this.loadHistory();
                this.setupMusicPlayer();
                this.setupMobileLayout();
            }, 100);
        } catch (error) {
            console.error('Initialization error:', error);
            // Force show app even if there are errors
            this.forceShowApp();
        }
    }

    // Loading and initialization
    showApp() {
        // Shorter timeout to prevent getting stuck
        setTimeout(() => {
            this.forceShowApp();
        }, 1000);
    }

    forceShowApp() {
        const loadingScreen = document.getElementById('loadingScreen');
        const app = document.getElementById('app');
        
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
        
        if (app) {
            app.classList.remove('hidden');
            app.style.opacity = '1';
            app.style.visibility = 'visible';
        }
        
        this.animateElementsIn();
    }

    animateElementsIn() {
        if (!this.animationsEnabled || this.animationPreference === 'essential') return;
        
        const elements = document.querySelectorAll('.card, .history-panel');
        elements.forEach((el, index) => {
            if (el) {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                
                setTimeout(() => {
                    el.style.transition = 'all 0.6s ease-out';
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }

    // Mobile layout setup
    setupMobileLayout() {
        const historyPanel = document.getElementById('historyPanel');
        if (window.innerWidth <= 768 && historyPanel) {
            historyPanel.classList.add('collapsed');
            this.isHistoryCollapsed = true;
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768 && !this.isHistoryCollapsed) {
                this.collapseHistory();
            }
        });
    }

    // Event listeners
    setupEventListeners() {
        try {
            // File upload - Fix the issue
            this.setupFileUpload();
            
            // Form interactions
            const unitToggle = document.getElementById('unitToggle');
            if (unitToggle) {
                unitToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleHeightUnit();
                });
            }
            
            const generateBtn = document.getElementById('generateBtn');
            if (generateBtn) {
                generateBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.generateChoreography();
                });
            }
            
            // Settings
            const settingsBtn = document.getElementById('settingsBtn');
            if (settingsBtn) {
                settingsBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.openSettings();
                });
            }
            
            const closeModalBtn = document.getElementById('closeModalBtn');
            if (closeModalBtn) {
                closeModalBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.closeSettings();
                });
            }
            
            const modalOverlay = document.getElementById('modalOverlay');
            if (modalOverlay) {
                modalOverlay.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.closeSettings();
                });
            }
            
            // History
            const clearHistoryBtn = document.getElementById('clearHistoryBtn');
            if (clearHistoryBtn) {
                clearHistoryBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.clearHistory();
                });
            }

            const collapseHistoryBtn = document.getElementById('collapseHistoryBtn');
            if (collapseHistoryBtn) {
                collapseHistoryBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleHistory();
                });
            }
            
            // Mobile menu
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            if (mobileMenuBtn) {
                mobileMenuBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleMobileMenu();
                });
            }

            // Export button
            const exportBtn = document.getElementById('exportBtn');
            if (exportBtn) {
                exportBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.exportToPDF();
                });
            }

            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeSettings();
                } else if (e.code === 'Space' && this.audioElement && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'SELECT') {
                    e.preventDefault();
                    this.togglePlayPause();
                }
            });
        } catch (error) {
            console.error('Event listener setup error:', error);
        }
    }

    // Music Player Setup
    setupMusicPlayer() {
        try {
            this.audioElement = document.getElementById('audioElement');
            if (!this.audioElement) return;

            // Audio event listeners
            this.audioElement.addEventListener('loadedmetadata', () => {
                this.duration = this.audioElement.duration || 0;
                this.updateTimeDisplay();
                this.detectMusicProperties();
            });

            this.audioElement.addEventListener('timeupdate', () => {
                this.currentTime = this.audioElement.currentTime || 0;
                this.updateProgress();
                this.updateStickyProgress();
            });

            this.audioElement.addEventListener('ended', () => {
                this.isPlaying = false;
                this.updatePlayButton();
                this.hideStickyPlayer();
            });

            this.audioElement.addEventListener('error', (e) => {
                console.error('Audio error:', e);
                this.showToast('Error loading audio file', 'error');
            });

            // Player controls
            const playPauseBtn = document.getElementById('playPauseBtn');
            if (playPauseBtn) {
                playPauseBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.togglePlayPause();
                });
            }

            const skipBackBtn = document.getElementById('skipBackBtn');
            if (skipBackBtn) {
                skipBackBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.skipTime(-10);
                });
            }

            const skipForwardBtn = document.getElementById('skipForwardBtn');
            if (skipForwardBtn) {
                skipForwardBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.skipTime(10);
                });
            }

            const volumeSlider = document.getElementById('volumeSlider');
            if (volumeSlider) {
                volumeSlider.addEventListener('input', (e) => {
                    this.setVolume(parseFloat(e.target.value));
                });
                volumeSlider.value = this.volume;
            }

            const progressBar = document.getElementById('progressBar');
            if (progressBar) {
                progressBar.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.seekToPosition(e);
                });
            }

            // Sticky player controls
            const stickyPlayPause = document.getElementById('stickyPlayPause');
            if (stickyPlayPause) {
                stickyPlayPause.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.togglePlayPause();
                });
            }
        } catch (error) {
            console.error('Music player setup error:', error);
        }
    }

    // File upload handling - FIXED
    setupFileUpload() {
        try {
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('musicFile');
            const selectFileBtn = document.getElementById('selectFileBtn');
            const removeFileBtn = document.getElementById('removeFile');

            // Fix: Make sure the file input click event is properly bound
            if (selectFileBtn && fileInput) {
                selectFileBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Select file button clicked');
                    fileInput.click();
                });
            }

            // Also make the upload area clickable
            if (uploadArea && fileInput) {
                uploadArea.addEventListener('click', (e) => {
                    // Only trigger if clicking on the upload area itself, not child elements
                    if (e.target === uploadArea || e.target.closest('.upload-content')) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Upload area clicked');
                        fileInput.click();
                    }
                });
            }
            
            if (removeFileBtn) {
                removeFileBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.removeFile();
                });
            }

            if (fileInput) {
                fileInput.addEventListener('change', (e) => {
                    console.log('File input changed:', e.target.files);
                    if (e.target.files && e.target.files.length > 0) {
                        this.handleFileSelect(e.target.files[0]);
                    }
                });
            }

            // Drag and drop
            if (uploadArea) {
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('drag-over');
                });

                uploadArea.addEventListener('dragleave', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('drag-over');
                });

                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('drag-over');
                    const file = e.dataTransfer.files[0];
                    if (file && file.type.startsWith('audio/')) {
                        this.handleFileSelect(file);
                    } else {
                        this.showToast('Please select a valid audio file', 'error');
                    }
                });
            }
        } catch (error) {
            console.error('File upload setup error:', error);
        }
    }

    handleFileSelect(file) {
        console.log('Handling file select:', file);
        if (!file) return;

        if (!file.type.startsWith('audio/')) {
            this.showToast('Please select a valid audio file', 'error');
            return;
        }

        const uploadContent = document.querySelector('.upload-content');
        const filePreview = document.getElementById('filePreview');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
        if (uploadContent) uploadContent.classList.add('hidden');
        if (filePreview) filePreview.classList.remove('hidden');

        // Load audio file
        try {
            const url = URL.createObjectURL(file);
            if (this.audioElement) {
                this.audioElement.src = url;
                this.audioElement.load();
            }
        } catch (error) {
            console.error('Error loading audio file:', error);
            this.showToast('Error loading audio file', 'error');
            return;
        }

        this.showToast('Music file uploaded successfully!', 'success');
    }

    removeFile() {
        const uploadContent = document.querySelector('.upload-content');
        const filePreview = document.getElementById('filePreview');
        const fileInput = document.getElementById('musicFile');

        if (fileInput) fileInput.value = '';
        if (uploadContent) uploadContent.classList.remove('hidden');
        if (filePreview) filePreview.classList.add('hidden');

        // Stop and reset audio
        if (this.audioElement) {
            this.audioElement.pause();
            this.audioElement.src = '';
            this.isPlaying = false;
            this.hideStickyPlayer();
            this.updatePlayButton();
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Music Player Methods
    togglePlayPause() {
        if (!this.audioElement || !this.audioElement.src) {
            this.showToast('Please upload a music file first', 'info');
            return;
        }

        if (this.isPlaying) {
            this.audioElement.pause();
            this.isPlaying = false;
            this.hideStickyPlayer();
        } else {
            const playPromise = this.audioElement.play();
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        this.isPlaying = true;
                        this.showStickyPlayer();
                    })
                    .catch(error => {
                        console.error('Error playing audio:', error);
                        this.showToast('Error playing audio file', 'error');
                    });
            }
        }
        this.updatePlayButton();
        this.animateWaveform();
    }

    skipTime(seconds) {
        if (!this.audioElement || !this.duration) return;
        this.audioElement.currentTime = Math.max(0, Math.min(this.duration, this.audioElement.currentTime + seconds));
    }

    setVolume(volume) {
        this.volume = volume;
        if (this.audioElement) {
            this.audioElement.volume = volume;
        }
    }

    seekToPosition(e) {
        if (!this.audioElement || !this.duration) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        this.audioElement.currentTime = percent * this.duration;
    }

    updatePlayButton() {
        const playIcon = document.querySelector('.play-icon');
        const pauseIcon = document.querySelector('.pause-icon');
        const stickyPlayPause = document.getElementById('stickyPlayPause');

        if (playIcon && pauseIcon) {
            if (this.isPlaying) {
                playIcon.classList.add('hidden');
                pauseIcon.classList.remove('hidden');
            } else {
                playIcon.classList.remove('hidden');
                pauseIcon.classList.add('hidden');
            }
        }

        if (stickyPlayPause) {
            stickyPlayPause.textContent = this.isPlaying ? '⏸️' : '▶️';
        }
    }

    updateProgress() {
        if (!this.duration) return;
        const percent = (this.currentTime / this.duration) * 100;
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        this.updateTimeDisplay();
    }

    updateStickyProgress() {
        if (!this.duration) return;
        const percent = (this.currentTime / this.duration) * 100;
        const stickyProgressFill = document.getElementById('stickyProgressFill');
        if (stickyProgressFill) {
            stickyProgressFill.style.width = `${percent}%`;
        }
    }

    updateTimeDisplay() {
        const currentTimeEl = document.getElementById('currentTime');
        const totalTimeEl = document.getElementById('totalTime');
        
        if (currentTimeEl) currentTimeEl.textContent = this.formatTime(this.currentTime);
        if (totalTimeEl) totalTimeEl.textContent = this.formatTime(this.duration);
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    showStickyPlayer() {
        const stickyPlayer = document.getElementById('stickyPlayer');
        const nowPlayingText = document.getElementById('nowPlayingText');
        const fileName = document.getElementById('fileName');
        
        if (stickyPlayer) {
            stickyPlayer.classList.remove('hidden');
        }
        
        if (nowPlayingText && fileName) {
            nowPlayingText.textContent = fileName.textContent || 'Now Playing';
        }
    }

    hideStickyPlayer() {
        const stickyPlayer = document.getElementById('stickyPlayer');
        if (stickyPlayer) {
            stickyPlayer.classList.add('hidden');
        }
    }

    animateWaveform() {
        const waveBars = document.querySelectorAll('.wave-bar');
        waveBars.forEach((bar) => {
            if (this.isPlaying) {
                bar.style.animationPlayState = 'running';
            } else {
                bar.style.animationPlayState = 'paused';
            }
        });
    }

    detectMusicProperties() {
        // Simulate music analysis
        setTimeout(() => {
            this.bpm = Math.floor(Math.random() * (140 - 60) + 60);
            const genres = ['Pop', 'Rock', 'Electronic', 'Hip-Hop', 'Jazz', 'Classical', 'Folk', 'R&B'];
            this.genre = genres[Math.floor(Math.random() * genres.length)];
            
            const bpmValue = document.getElementById('bpmValue');
            const genreValue = document.getElementById('genreValue');
            
            if (bpmValue) bpmValue.textContent = this.bpm;
            if (genreValue) genreValue.textContent = this.genre;
        }, 2000);
    }

    // Dance styles population - FIXED
    populateDanceStyles() {
        console.log('Populating dance styles...');
        const select = document.getElementById('danceStyle');
        if (!select) {
            console.error('Dance style select element not found');
            return;
        }
        
        try {
            // Clear existing options except the first one
            const firstOption = select.firstElementChild;
            select.innerHTML = '';
            if (firstOption) {
                select.appendChild(firstOption);
            }
            
            danceStyles.forEach(category => {
                console.log('Adding category:', category.category);
                const optgroup = document.createElement('optgroup');
                optgroup.label = category.category;
                
                category.styles.forEach((style) => {
                    const option = document.createElement('option');
                    option.value = style;
                    option.textContent = style;
                    optgroup.appendChild(option);
                    if(style != "Hip-Hop") {
                        option.style.filter = "blur(2px)";   // blur effect
                        option.style.color = "#999";         // lighter text
                        option.disabled = "true"; // prevent clicking
                        option.innerHTML = style + '🔒';
                    }
                });
                
                select.appendChild(optgroup);
            });
            
            console.log('Dance styles populated successfully');
        } catch (error) {
            console.error('Error populating dance styles:', error);
        }
    }

    // Height unit toggle
    toggleHeightUnit() {
        const toggle = document.getElementById('unitToggle');
        const heightInput = document.getElementById('height');
        
        if (!toggle || !heightInput) return;
        
        if (this.heightUnit === 'cm') {
            this.heightUnit = 'ft';
            toggle.textContent = 'ft';
            toggle.dataset.unit = 'ft';
            heightInput.placeholder = "5'8\"";
        } else {
            this.heightUnit = 'cm';
            toggle.textContent = 'cm';
            toggle.dataset.unit = 'cm';
            heightInput.placeholder = '170';
        }
        
        this.showToast(`Height unit changed to ${this.heightUnit}`, 'info');
    }

    // Generate choreography
    async generateChoreography() {
        if (this.isGenerating) return;

        // Validate form
        const musicFile = document.getElementById('musicFile');
        const danceStyle = document.getElementById('danceStyle');
        const age = document.getElementById('age');
        const height = document.getElementById('height');

        if (!musicFile || !musicFile.files || musicFile.files.length === 0) {
            this.showToast('Please upload a music file', 'error');
            return;
        }

        if (!danceStyle || !danceStyle.value) {
            this.showToast('Please select a dance style', 'error');
            return;
        }

        if (!age || !age.value) {
            this.showToast('Please enter your age', 'error');
            return;
        }

        if (!height || !height.value) {
            this.showToast('Please enter your height', 'error');
            return;
        }

        const ageValue = parseInt(age.value);
        if (ageValue < 5 || ageValue > 100) {
            this.showToast('Please enter a valid age (5-100)', 'error');
            return;
        }

        this.isGenerating = true;
        this.showGeneratingState();

        try {
            // Simulate AI generation
            await this.simulateGeneration();

            // Create result
            const result = this.createGenerationResult(
                musicFile.files[0].name, 
                danceStyle.value, 
                ageValue, 
                height.value
            );
            
            this.showVideoStepResult(result);
            this.addToHistory(result);
            
        } catch (error) {
            console.error('Generation error:', error);
            this.showToast('Failed to generate choreography. Please try again.', 'error');
        } finally {
            this.isGenerating = false;
            this.hideGeneratingState();
        }
    }

    showGeneratingState() {
        const btn = document.getElementById('generateBtn');
        const btnText = btn?.querySelector('.btn-text');
        const btnLoading = btn?.querySelector('.btn-loading');

        if (btnText) btnText.classList.add('hidden');
        if (btnLoading) btnLoading.classList.remove('hidden');
        if (btn) btn.style.pointerEvents = 'none';
    }

    hideGeneratingState() {
        const btn = document.getElementById('generateBtn');
        const btnText = btn?.querySelector('.btn-text');
        const btnLoading = btn?.querySelector('.btn-loading');

        if (btnText) btnText.classList.remove('hidden');
        if (btnLoading) btnLoading.classList.add('hidden');
        if (btn) btn.style.pointerEvents = 'auto';
    }

    async simulateGeneration() {
        return new Promise(resolve => {
            setTimeout(resolve, 3000 + Math.random() * 2000);
        });
    }

    createGenerationResult(musicName, style, age, height) {
        const videoSteps = this.generateVideoSteps(style);
        
        return {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            music: musicName,
            style: style,
            age: parseInt(age),
            choreography_style: `${height}`,
            videoSteps: videoSteps,
            quality: this.videoQuality
        };
    }

    generateVideoSteps(style) {
        const stepTemplates = {
            'Bharatanatyam': [
                { title: 'Warm-up and Basic Position', duration: '0:45', description: 'Start with gentle stretches and establish your base stance with proper Araimandi position' },
                { title: 'Namaskaram Sequence', duration: '1:20', description: 'Learn the traditional greeting with precise hand movements and devotional expressions' },
                { title: 'Basic Adavu Patterns', duration: '1:30', description: 'Master fundamental stepping patterns with synchronized arm movements' },
                { title: 'Mudra Integration', duration: '1:15', description: 'Incorporate classical hand gestures to tell the story through movement' },
                { title: 'Expression and Abhinaya', duration: '1:45', description: 'Add facial expressions and emotional depth to your performance' },
                { title: 'Complete Tillana', duration: '2:30', description: 'Put all elements together for the full rhythmic sequence' }
            ],
            'Hip-Hop': [
                { title: 'Basic Groove Foundation', duration: '0:50', description: 'Establish your bounce and connect with the beat naturally' },
                { title: 'Isolation Techniques', duration: '1:10', description: 'Master head, shoulder, and chest isolations for authentic style' },
                { title: 'Top Rock Basics', duration: '1:25', description: 'Learn standing dance moves and footwork patterns' },
                { title: 'Breaking Fundamentals', duration: '1:40', description: 'Introduction to basic floor work and transitions' },
                { title: 'Freestyle Flow', duration: '1:30', description: 'Develop personal style and improvisation skills' },
                { title: 'Battle Ready Combo', duration: '2:00', description: 'Complete routine with attitude and performance energy' }
            ],
            'Ballet': [
                { title: 'Barre Warm-up', duration: '1:00', description: 'Essential stretching and alignment preparation at the barre' },
                { title: 'Basic Positions', duration: '1:15', description: 'Master the five fundamental positions of feet and arms' },
                { title: 'Port de Bras', duration: '1:20', description: 'Graceful arm movements and upper body coordination' },
                { title: 'Adagio Combinations', duration: '1:45', description: 'Slow, controlled movements building strength and balance' },
                { title: 'Allegro Preparations', duration: '1:35', description: 'Jump preparations and basic traveling movements' },
                { title: 'Grand Finale', duration: '2:15', description: 'Complete enchainement with leaps, turns, and reverence' }
            ],
            'Salsa': [
                { title: 'Basic Salsa Step', duration: '0:55', description: 'Master the fundamental 1-2-3, 5-6-7 rhythm and timing' },
                { title: 'Cross Body Lead', duration: '1:25', description: 'Learn the essential partner traveling movement' },
                { title: 'Right and Left Turns', duration: '1:30', description: 'Smooth turning techniques for both partners' },
                { title: 'Shines and Footwork', duration: '1:20', description: 'Solo sections with intricate foot patterns' },
                { title: 'Advanced Combinations', duration: '1:50', description: 'Complex turn patterns and styling elements' },
                { title: 'Performance Routine', duration: '2:20', description: 'Complete social dance sequence with flair and attitude' }
            ]
        };

        const defaultSteps = [
            { title: 'Foundation and Warm-up', duration: '0:45', description: 'Begin with proper posture, breathing, and gentle preparation movements' },
            { title: 'Basic Movement Patterns', duration: '1:15', description: 'Learn the core steps and rhythm specific to your chosen style' },
            { title: 'Coordination Building', duration: '1:30', description: 'Integrate upper and lower body movements with musicality' },
            { title: 'Intermediate Techniques', duration: '1:40', description: 'Add complexity with turns, jumps, or style-specific elements' },
            { title: 'Expression and Flow', duration: '1:25', description: 'Develop personal interpretation and smooth transitions' },
            { title: 'Complete Routine', duration: '2:30', description: 'Put all elements together in a polished performance sequence' }
        ];

        return stepTemplates[style] || defaultSteps;
    }

    showVideoStepResult(result) {
        const resultCard = document.getElementById('resultCard');
        const resultContent = document.getElementById('resultContent');

        if (!resultCard || !resultContent) return;

        const resultHTML = `
            <div class="result-info" style="padding: 1.5rem; background: var(--color-bg-3); border-radius: var(--border-radius-sm); margin-bottom: 2rem;">
                <h4>${result.style} Video Choreography</h4>
                <p><strong>Music:</strong> ${result.music}</p>
                <p><strong>Age:</strong> ${result.age} years | <strong>Choreography Style:</strong> ${result.height}</p>
                <p><strong>Quality:</strong> ${result.quality} | <strong>Steps:</strong> ${result.videoSteps.length} videos</p>
            </div>
            
            <div class="video-steps-grid">
                ${result.videoSteps.map((step, index) => `
                    <div class="video-step-card" data-step="${index + 1}">
                        <div class="step-number">${index + 1}</div>
                        <div class="video-thumbnail" onclick="window.danceAI.playVideoStep(${index + 1})">
                            <div class="video-placeholder">🎬</div>
                            <div class="video-duration">${step.duration}</div>
                            <div class="watch-button">▶</div>
                        </div>
                        <div class="step-title">Step ${index + 1}: ${step.title}</div>
                        <div class="step-description">${step.description}</div>
                        <div class="step-progress">
                            <div class="step-progress-fill" style="width: 0%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        resultContent.innerHTML = resultHTML;
        resultCard.classList.remove('hidden');
        
        if (this.animationsEnabled && this.animationPreference !== 'essential') {
            resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        this.showToast('Video choreography generated successfully!', 'success');
    }

    playVideoStep(stepNumber) {
        // Simulate video step playback
        this.showToast(`Playing Step ${stepNumber} video tutorial`, 'info');
        
        // Animate progress bar for the step
        const stepCard = document.querySelector(`[data-step="${stepNumber}"]`);
        const progressFill = stepCard?.querySelector('.step-progress-fill');
        
        if (progressFill) {
            progressFill.style.width = '0%';
            setTimeout(() => {
                progressFill.style.width = '100%';
            }, 100);
        }
    }

    exportToPDF() {
        this.showToast('Exporting choreography to PDF...', 'info');
        
        // Simulate PDF generation
        setTimeout(() => {
            this.showToast('PDF export completed successfully!', 'success');
        }, 2000);
    }

    // History management
    toggleHistory() {
        const historyPanel = document.getElementById('historyPanel');
        const collapseBtn = document.getElementById('collapseHistoryBtn');
        
        if (!historyPanel) return;

        this.isHistoryCollapsed = !this.isHistoryCollapsed;
        
        if (this.isHistoryCollapsed) {
            historyPanel.classList.add('collapsed');
            if (collapseBtn) collapseBtn.innerHTML = '<span class="icon">📂</span>';
        } else {
            historyPanel.classList.remove('collapsed');
            if (collapseBtn) collapseBtn.innerHTML = '<span class="icon">📁</span>';
        }
    }

    collapseHistory() {
        const historyPanel = document.getElementById('historyPanel');
        const collapseBtn = document.getElementById('collapseHistoryBtn');
        
        if (historyPanel) {
            historyPanel.classList.add('collapsed');
            this.isHistoryCollapsed = true;
            if (collapseBtn) collapseBtn.innerHTML = '<span class="icon">📂</span>';
        }
    }

    addToHistory(result) {
        this.history.unshift(result);
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
        this.saveHistory();
        this.renderHistory();
    }

    renderHistory() {
        const historyContent = document.getElementById('historyContent');
        if (!historyContent) return;
        
        if (this.history.length === 0) {
            historyContent.innerHTML = `
                <div class="history-empty">
                    <div class="empty-icon">📝</div>
                    <p>No dance generations yet</p>
                </div>
            `;
            return;
        }

        const historyHTML = this.history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <h4>${item.style}</h4>
                <p>Age: ${item.age} | Choreography_style: ${item.height}</p>
                <p>Music: ${item.music}</p>
                <div class="history-item-time">
                    ${this.formatDate(item.timestamp)}
                </div>
            </div>
        `).join('');

        historyContent.innerHTML = historyHTML;

        // Add click listeners to history items
        document.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = parseInt(item.dataset.id);
                const historyItem = this.history.find(h => h.id === id);
                if (historyItem) {
                    this.showVideoStepResult(historyItem);
                }
            });
        });
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear all history?')) {
            this.history = [];
            this.saveHistory();
            this.renderHistory();
            this.showToast('History cleared', 'info');
        }
    }

    formatDate(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);

        if (diffHours < 1) {
            return 'Just now';
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    // Settings management
    populateSettingsOptions() {
        try {
            this.populateThemeOptions();
            this.populateColorOptions();
            this.populateAnimationOptions();
            this.populateQualityOptions();
        } catch (error) {
            console.error('Error populating settings:', error);
        }
    }

    populateThemeOptions() {
        const themeGrid = document.getElementById('themeGrid');
        if (!themeGrid) return;

        themeGrid.innerHTML = '';
        
        themes.forEach(theme => {
            const option = document.createElement('div');
            option.className = 'theme-option';
            option.dataset.theme = theme.name;
            option.innerHTML = `<span>${theme.name}</span>`;
            
            if (theme.name === this.currentTheme) {
                option.classList.add('active');
            }
            
            option.addEventListener('click', () => this.selectTheme(theme.name));
            themeGrid.appendChild(option);
        });
    }

    populateColorOptions() {
        const colorGrid = document.getElementById('colorGrid');
        if (!colorGrid) return;

        colorGrid.innerHTML = '';

        colorSchemes.forEach(scheme => {
            const option = document.createElement('div');
            option.className = 'color-option';
            option.dataset.color = scheme.name;
            option.innerHTML = `
                <div class="color-preview" style="background: ${scheme.accent}"></div>
                <span>${scheme.name}</span>
            `;
            
            if (scheme.name === this.currentColorScheme) {
                option.classList.add('active');
            }
            
            option.addEventListener('click', () => this.selectColorScheme(scheme.name));
            colorGrid.appendChild(option);
        });
    }

    populateAnimationOptions() {
        const animationOptionsEl = document.getElementById('animationOptions');
        if (!animationOptionsEl) return;

        animationOptionsEl.innerHTML = '';

        animationOptions.forEach(option => {
            const optionEl = document.createElement('div');
            optionEl.className = 'animation-option';
            optionEl.dataset.animation = option.value;
            optionEl.innerHTML = `<span>${option.name}</span>`;
            
            if (option.value === this.animationPreference) {
                optionEl.classList.add('active');
            }
            
            optionEl.addEventListener('click', () => this.selectAnimationPreference(option.value));
            animationOptionsEl.appendChild(optionEl);
        });
    }

    populateQualityOptions() {
        const qualityOptionsEl = document.getElementById('qualityOptions');
        if (!qualityOptionsEl) return;

        qualityOptionsEl.innerHTML = '';

        qualityOptions.forEach(option => {
            const optionEl = document.createElement('div');
            optionEl.className = 'quality-option';
            optionEl.dataset.quality = option.value;
            optionEl.innerHTML = `<span>${option.name}</span>`;
            
            if (option.value === this.videoQuality) {
                optionEl.classList.add('active');
            }
            
            optionEl.addEventListener('click', () => this.selectVideoQuality(option.value));
            qualityOptionsEl.appendChild(optionEl);
        });
    }

    selectTheme(themeName) {
        this.currentTheme = themeName;
        this.applyTheme();
        this.saveSettings();
        
        // Update active states
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.theme === themeName) {
                option.classList.add('active');
            }
        });
        
        this.showToast(`${themeName} theme applied`, 'success');
    }

    selectColorScheme(schemeName) {
        this.currentColorScheme = schemeName;
        this.applyColorScheme();
        this.saveSettings();
        
        // Update active states
        document.querySelectorAll('.color-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.color === schemeName) {
                option.classList.add('active');
            }
        });
        
        this.showToast(`${schemeName} color scheme applied`, 'success');
    }

    selectAnimationPreference(preference) {
        this.animationPreference = preference;
        this.animationsEnabled = preference !== 'essential';
        this.updateAnimationSpeed();
        this.saveSettings();

        // Update active states
        document.querySelectorAll('.animation-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.animation === preference) {
                option.classList.add('active');
            }
        });

        this.showToast(`Animation preference updated to ${preference}`, 'success');
    }

    selectVideoQuality(quality) {
        this.videoQuality = quality;
        this.saveSettings();

        // Update active states
        document.querySelectorAll('.quality-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.quality === quality) {
                option.classList.add('active');
            }
        });

        this.showToast(`Video quality set to ${quality}`, 'success');
    }

    applyTheme() {
        const theme = themes.find(t => t.name === this.currentTheme) || themes[0];
        
        if (theme.name === 'Auto') {
            // Use system preference
            document.body.removeAttribute('data-theme');
        } else {
            document.body.dataset.theme = theme.name.toLowerCase();
        }
        
        if (theme.primary !== 'auto') {
            this.applyCustomTheme(theme);
        }
    }

    applyColorScheme() {
        const scheme = colorSchemes.find(s => s.name === this.currentColorScheme);
        if (!scheme) return;

        const root = document.documentElement;
        root.style.setProperty('--theme-primary', scheme.primary);
        root.style.setProperty('--theme-secondary', scheme.secondary);
        root.style.setProperty('--theme-accent', scheme.accent);
    }

    applyCustomTheme(theme) {
        const root = document.documentElement;
        root.style.setProperty('--theme-primary', theme.primary);
        root.style.setProperty('--theme-secondary', theme.secondary);
        root.style.setProperty('--theme-accent', theme.accent);
        
        // Update text colors based on theme
        if (this.currentTheme === 'Light') {
            root.style.setProperty('--theme-text', '#1e293b');
            root.style.setProperty('--theme-text-secondary', '#64748b');
            root.style.setProperty('--theme-border', 'rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--theme-glass', 'rgba(255, 255, 255, 0.8)');
            root.style.setProperty('--theme-glass-border', 'rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--theme-shadow', 'rgba(0, 0, 0, 0.1)');
        } else {
            root.style.setProperty('--theme-text', '#ffffff');
            root.style.setProperty('--theme-text-secondary', '#b8bcc8');
            root.style.setProperty('--theme-border', 'rgba(255, 255, 255, 0.1)');
            root.style.setProperty('--theme-glass', 'rgba(255, 255, 255, 0.05)');
            root.style.setProperty('--theme-glass-border', 'rgba(255, 255, 255, 0.1)');
            root.style.setProperty('--theme-shadow', 'rgba(0, 0, 0, 0.3)');
        }
    }

    updateAnimationSpeed() {
        const root = document.documentElement;
        let speed = '1';
        
        if (this.animationPreference === 'reduced') {
            speed = '0.5';
        } else if (this.animationPreference === 'essential') {
            speed = '0';
        }
        
        root.style.setProperty('--animation-speed', speed);
    }

    openSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    closeSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    // Mobile menu
    toggleMobileMenu() {
        const historyPanel = document.getElementById('historyPanel');
        if (historyPanel) {
            historyPanel.classList.toggle('open');
        }
    }

    // Toast notifications
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // Local storage (Note: Using fallback for sandbox environment)
    saveSettings() {
        const settings = {
            theme: this.currentTheme,
            colorScheme: this.currentColorScheme,
            animationPreference: this.animationPreference,
            videoQuality: this.videoQuality,
            animationsEnabled: this.animationsEnabled
        };
        
        // Store in memory as fallback
        this.settingsCache = settings;
    }

    loadSettings() {
        // Load from memory cache as fallback
        if (this.settingsCache) {
            const settings = this.settingsCache;
            this.currentTheme = settings.theme || 'Dark';
            this.currentColorScheme = settings.colorScheme || 'Cosmic Purple';
            this.animationPreference = settings.animationPreference || 'full';
            this.videoQuality = settings.videoQuality || '720p';
            this.animationsEnabled = settings.animationsEnabled !== false;
        }
        
        this.applyTheme();
        this.applyColorScheme();
        this.updateAnimationSpeed();
    }

    saveHistory() {
        // Store in memory as fallback
        this.historyCache = this.history;
    }

    loadHistory() {
        // Load from memory cache as fallback
        if (this.historyCache) {
            this.history = this.historyCache;
        }
        this.renderHistory();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.danceAI = new DanceAIApp();
    } catch (error) {
        console.error('Failed to initialize app:', error);
        // Force show app if initialization fails
        setTimeout(() => {
            const loadingScreen = document.getElementById('loadingScreen');
            const app = document.getElementById('app');
            
            if (loadingScreen) loadingScreen.style.display = 'none';
            if (app) {
                app.classList.remove('hidden');
                app.style.opacity = '1';
                app.style.visibility = 'visible';
            }
        }, 1000);
    }
});

// Handle page visibility for animations
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        document.documentElement.style.setProperty('--animation-speed', '0');
    } else if (window.danceAI?.animationsEnabled) {
        const speed = window.danceAI.animationPreference === 'reduced' ? '0.5' : '1';
        document.documentElement.style.setProperty('--animation-speed', speed);
    }
});
