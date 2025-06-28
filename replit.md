# Home Assistant Telegram Bot

## Overview

This is a production-ready Flask-based web application that integrates with Home Assistant and provides a Telegram bot interface for controlling smart home devices. The system features a web dashboard, a Home Assistant API client, a Telegram bot, and a comprehensive monitoring system with OpenMetrics integration. It provides both web and chat-based interfaces for home automation control with real-time metrics and performance monitoring.

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
- Real-time metrics dashboard with auto-refresh
- OpenMetrics endpoint for Prometheus integration
- Responsive design with dark theme UI

### Telegram Bot Integration
- Uses python-telegram-bot library for Telegram API communication
- Supports device control commands (lights, switches)
- Provides system status and sensor information
- Command-based interface for home automation
- Comprehensive metrics tracking for all bot commands
- Performance monitoring with execution time tracking

### Home Assistant API Client
- RESTful API communication with Home Assistant instance
- Bearer token authentication
- Handles entity state retrieval and device control
- Error handling and logging for API interactions
- API performance monitoring and health checks
- Device command tracking with success/failure metrics

### OpenMetrics Monitoring System
- Production-ready metrics collection using prometheus_client
- Tracks application uptime, memory usage, and performance
- Monitors Telegram bot command usage and response times
- Home Assistant API request tracking with status codes
- Device operation monitoring (lights, switches, sensors)
- Active user tracking and connection health monitoring
- Web dashboard integration with real-time metric updates

### Frontend Design
- Bootstrap 5 with custom dark theme
- Font Awesome icons for enhanced UI
- Responsive grid layout
- Card-based component design
- Real-time metrics visualization
- Dynamic content updates via JavaScript

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
- **prometheus_client**: OpenMetrics and Prometheus integration for monitoring

### UI Dependencies
- **Bootstrap 5**: Frontend CSS framework with dark theme
- **Font Awesome**: Icon library for enhanced UI

### Monitoring Dependencies
- **prometheus_client**: Metrics collection and exposition
- **psutil** (via metrics): System resource monitoring
- **threading**: Multi-threaded metrics server

### Infrastructure
- **OpenSSL**: Secure communication support

## Deployment Strategy

### Replit Deployment (Recommended)
- **Autoscale deployment target** for automatic scaling
- **Gunicorn WSGI server** binding to 0.0.0.0:5000
- **Environment-based configuration** for Home Assistant connection
- **Multi-process support** with reload capabilities for development
- **No database dependencies** - minimal setup required

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
- June 27, 2025: Implemented smart device state checking to prevent unnecessary API calls and HTTP 500 errors
- June 27, 2025: Added intelligent error handling for grouped light devices (like Yeelight groups)
- June 27, 2025: Improved user feedback with device state awareness (already on/off notifications)
- June 27, 2025: Implemented comprehensive OpenMetrics monitoring system with prometheus_client integration
- June 27, 2025: Added real-time metrics dashboard to web interface with auto-updating performance indicators
- June 27, 2025: Integrated metrics tracking for all Telegram bot commands and Home Assistant API calls
- June 27, 2025: Created /metrics endpoint for Prometheus scraping and /api/metrics-summary for dashboard consumption
- June 28, 2025: Removed PostgreSQL database dependencies and Docker configurations to simplify deployment

## User Preferences

Preferred communication style: Simple, everyday language.