"""Application settings and color scheme."""

COLORS = {
    "primary": "#a23b84",        # Primary purple - buttons, accents
    "secondary": "#3a2b95",      # Headers, secondary elements
    "tertiary": "#6f2fa6",       # Gradients, highlights
    "dark_bg": "#1a1a2e",        # Main background
    "dark_card": "#16213e",      # Card backgrounds
    "dark_input": "#0f3460",     # Input fields
    "text": "#ffffff",           # Primary text
    "text_muted": "#b8b8b8",     # Secondary text
    "success": "#28a745",        # Success states
    "warning": "#ffc107",        # Warning states
    "error": "#dc3545",          # Error states
}

APP_SETTINGS = {
    "app_name": "Inclusive Design Wizard",
    "version": "1.0.0",
    "min_font_size": 16,
    "touch_target_min": 44,
    "focus_outline_width": 3,
    "database_path": "data/inclusive_design.db",
}

PHASES = {
    "context": {
        "name": "Context Gathering",
        "questions": [
            "What course or learning material are you designing?",
            "Who are your learners? Describe the group you're designing for.",
            "What are the primary learning objectives for this experience?",
            "What delivery format will you use (in-person, online, hybrid)?"
        ]
    },
    "learner_analysis": {
        "name": "Learner Analysis",
        "questions": [
            "What do you currently know about your learners' preferences and needs?",
            "How do you typically learn about accommodations needed by your learners?",
            "What barriers have you encountered before when trying to make learning accessible?",
            "What assumptions might you be making about your learners' abilities?"
        ]
    },
    "udl_engagement": {
        "name": "UDL: Engagement",
        "questions": [
            "How will learners see the relevance of this material to their own lives?",
            "What meaningful choices can learners make in how they engage with the material?",
            "How are you building community and collaboration among learners?",
            "How do you support learners' persistence when they encounter frustration?",
            "How do you foster self-reflection and metacognition?"
        ]
    },
    "udl_representation": {
        "name": "UDL: Representation",
        "questions": [
            "In how many different formats is information available (text, audio, video, etc.)?",
            "How do you support vocabulary and symbol comprehension?",
            "What scaffolds exist for activating or supplying background knowledge?",
            "How do you highlight patterns, critical features, and big ideas?"
        ]
    },
    "udl_expression": {
        "name": "UDL: Expression",
        "questions": [
            "What options exist for learners to demonstrate their knowledge?",
            "How can learners use different tools and media for communication?",
            "What scaffolds support planning, strategy development, and organizing?",
            "Are there flexible submission formats and timelines?",
            "How do learners receive and act on feedback?"
        ]
    },
    "wcag_review": {
        "name": "WCAG Review",
        "questions": [
            "Perceivable: Do all images have alt text? Is color contrast sufficient? Are there multiple formats for content?",
            "Operable: Is everything keyboard accessible? Are timing requirements adjustable? Is navigation consistent?",
            "Understandable: Is navigation clear and consistent? Are error messages helpful and specific?",
            "Robust: Does your content work with assistive technologies? Is it cross-platform compatible?"
        ]
    },
    "assessment": {
        "name": "Recommendations",
        "questions": [
            "How will you assess if your accessibility goals are being met?",
            "What feedback mechanisms exist for learners to report barriers?",
            "How will you iterate and improve based on feedback received?"
        ]
    }
}

PHASE_ORDER = [
    "context",
    "learner_analysis",
    "udl_engagement",
    "udl_representation",
    "udl_expression",
    "wcag_review",
    "assessment"
]
