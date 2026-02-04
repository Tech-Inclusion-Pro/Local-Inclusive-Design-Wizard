"""
py2app build script for Inclusive Design Wizard
Usage: python setup.py py2app
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('config', ['config/settings.py', 'config/ai_providers.py', 'config/__init__.py']),
    ('prompts', ['prompts/system_prompts.py', 'prompts/__init__.py']),
    ('core', ['core/database.py', 'core/auth.py', 'core/ai_manager.py', 'core/conversation.py', 'core/__init__.py']),
    ('ui', ['ui/main_window.py', 'ui/login.py', 'ui/dashboard.py', 'ui/chat.py', 'ui/settings.py', 'ui/styles.py', 'ui/__init__.py']),
    ('assets', ['assets/icon.png']),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icon.icns',
    'plist': {
        'CFBundleName': 'Inclusive Design Wizard',
        'CFBundleDisplayName': 'Inclusive Design Wizard',
        'CFBundleIdentifier': 'com.inclusivedesign.wizard',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.15',
    },
    'packages': ['PyQt6', 'sqlalchemy', 'bcrypt', 'aiohttp', 'docx', 'lxml'],
    'includes': [
        'config', 'config.settings', 'config.ai_providers',
        'prompts', 'prompts.system_prompts',
        'core', 'core.database', 'core.auth', 'core.ai_manager', 'core.conversation',
        'ui', 'ui.main_window', 'ui.login', 'ui.dashboard', 'ui.chat', 'ui.settings', 'ui.styles',
    ],
}

setup(
    name='Inclusive Design Wizard',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
