# Home Assistant Telegram Bot

## Overview

This is a Flask-based web application that integrates with Home Assistant and provides a Telegram bot interface for controlling smart home devices. The system consists of a web dashboard, a Home Assistant API client, and a Telegram bot that runs concurrently to provide both web and chat-based interfaces for home automation control.

## System Architecture

The application follows a modular architecture with separate components for different functionalities:

- **Flask Web Application** (`app.py`): Provides a web dashboard interface
- **Telegram Bot** (`bot.py`): Handles Telegram messaging and commands
- **Home Assistant API Client** (`home_assistant.py`): Manages communication with Home Assistant
- **Main Controller** (`main.py`): Orchestrates both Flask and Telegram bot execution

The system uses a multi-threaded approach where the Flask application runs in a separate thread while the Telegram bot runs in the main thread.

## Key Components

### Web Dashboard
- Built with Flask framework using Bootstrap dark theme
- Provides real-time system status and entity counts
- Displays light states and device information
- Responsive design with dark theme UI

### Telegram Bot Integration
- Uses python-telegram-bot library for Telegram API communication
- Supports device control commands (lights, switches)
- Provides system status and sensor information
- Command-based interface for home automation

### Home Assistant API Client
- RESTful API communication with Home Assistant instance
- Bearer token authentication
- Handles entity state retrieval and device control
- Error handling and logging for API interactions

### Frontend Design
- Bootstrap 5 with custom dark theme
- Font Awesome icons for enhanced UI
- Responsive grid layout
- Card-based component design

## Data Flow

1. **Web Interface**: User accesses Flask dashboard → Home Assistant API → Device states displayed
2. **Telegram Interface**: User sends bot command → Bot processes command → Home Assistant API → Device action executed → Confirmation sent to user
3. **Device Control**: Command received → API validation → Home Assistant service call → Device state change
4. **Status Updates**: Periodic API calls retrieve current device states for display

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for dashboard interface
- **python-telegram-bot**: Telegram bot API integration
- **requests**: HTTP client for Home Assistant API communication
- **gunicorn**: WSGI server for production deployment

### UI Dependencies
- **Bootstrap 5**: Frontend CSS framework with dark theme
- **Font Awesome**: Icon library for enhanced UI

### Infrastructure
- **PostgreSQL**: Database system (configured but not actively used in current codebase)
- **OpenSSL**: Secure communication support

## Deployment Strategy

The application is configured for Replit deployment with:

- **Autoscale deployment target** for automatic scaling
- **Gunicorn WSGI server** binding to 0.0.0.0:5000
- **Environment-based configuration** for Home Assistant connection
- **Multi-process support** with reload capabilities for development

Required environment variables:
- `HOME_ASSISTANT_URL`: Base URL for Home Assistant instance
- `HOME_ASSISTANT_TOKEN`: Bearer token for API authentication
- `TELEGRAM_BOT_TOKEN`: Telegram bot API token
- `SESSION_SECRET`: Flask session security key

## Changelog

- June 27, 2025: Initial setup and configuration
- June 27, 2025: Successfully connected to Home Assistant instance
- June 27, 2025: Fixed Telegram bot imports and dependencies
- June 27, 2025: Added Russian language support for bot commands (/start and /help)
- June 27, 2025: Implemented multi-process architecture for stable Telegram bot execution
- June 27, 2025: Added real-time service status monitoring on web dashboard
- June 27, 2025: Successfully deployed complete solution with both web interface and Telegram bot running simultaneously
- June 27, 2025: Fixed JSON parsing errors for large Home Assistant responses (715+ entities)
- June 27, 2025: Enhanced Telegram bot error handling with informative Russian messages
- June 27, 2025: Optimized /lights command to handle large device collections efficiently
- June 27, 2025: Implemented pagination for all device commands (/lights, /switches, /sensors)
- June 27, 2025: Fixed device control API responses and improved diagnostic logging
- June 27, 2025: Enhanced user experience with Russian language error messages and detailed feedback

## User Preferences

Preferred communication style: Simple, everyday language.