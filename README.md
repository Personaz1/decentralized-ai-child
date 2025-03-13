# Decentralized AI System

A powerful decentralized artificial intelligence system that combines multiple AI models for enhanced performance and reliability.

## System Requirements

### Minimum Requirements:
- Python 3.9+
- CUDA 11.8+
- 16GB+ RAM
- 100GB+ SSD
- Linux/Unix system

### Recommended Requirements:
- Python 3.9+
- CUDA 12.0+
- 32GB+ RAM
- 500GB+ SSD
- NVIDIA GPU with 8GB+ VRAM
- Linux/Unix system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/decentralized-ai.git
cd decentralized-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the system:
```bash
cp config/system_config.yaml.example config/system_config.yaml
# Edit config/system_config.yaml with your settings
```

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_llm_system.py -v

# Run tests with coverage
pytest --cov=src tests/
```

## Project Structure

```
decentralized-ai/
├── src/
│   ├── core/           # Core system components
│   ├── utils/          # Utility functions
│   ├── tests/          # Test suite
│   └── api/            # API endpoints
├── config/             # Configuration files
├── docs/               # Documentation
├── models/             # AI models
└── cache/              # Cache directory
```

## Key Features

- Self-analysis and improvement
- Self-evolution capabilities
- Automated testing and validation
- Security monitoring and protection
- LLM integration and management
- Distributed knowledge exchange
- Performance optimization
- Real-time monitoring

## Development

See [Development Guide](docs/development_guide.md) for detailed instructions on:
- Setting up the development environment
- Code style and standards
- Testing procedures
- Contributing guidelines

## Deployment

See [Deployment Guide](docs/deployment_guide.md) for instructions on:
- Server requirements
- Installation steps
- Configuration
- Monitoring setup
- Security measures
- Backup procedures

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 