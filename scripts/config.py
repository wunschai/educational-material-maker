"""Shared constants for educational_material_maker pipeline scripts."""

# Time buffer (seconds) added after each slide's audio duration.
# Used by render_video.py (video segment length) and generate_subtitles.py (SRT time offset).
# Changing this value affects both video pacing and subtitle synchronization.
SLIDE_BUFFER_SECONDS = 1.5
