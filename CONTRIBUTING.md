# Contributing to Gmail Summaries

Thank you for your interest in contributing to Gmail Summaries! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in the [GitHub Issues](https://github.com/murphy360/gmail_summaries/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment details (OS, Docker version, Python version)
   - Relevant logs or error messages

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/murphy360/gmail_summaries.git
   cd gmail_summaries
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Test the service locally
   python -m py_compile *.py
   
   # Test with Docker
   docker-compose build
   docker-compose up -d
   curl http://localhost:5000/health
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add docstrings to classes and functions
- Use type hints where appropriate

### Documentation

- Update README.md for user-facing changes
- Update SETUP.md for setup process changes
- Add inline comments for complex logic
- Update API documentation for endpoint changes

### Testing

- Test your changes thoroughly
- Verify Docker build succeeds
- Test API endpoints with curl
- Check logs for errors
- Test with different configurations

### Commit Messages

Use clear, descriptive commit messages:
- Good: "Add support for filtering emails by sender"
- Bad: "Update code"

Format:
```
Brief summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Include motivation for the change and contrast with previous behavior.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"
```

## Areas for Contribution

Here are some areas where contributions are especially welcome:

### Features

- Additional email filtering options (by sender, by date range, by label)
- Support for OAuth2 user authentication (in addition to service accounts)
- Webhook support for real-time email notifications
- Multiple email account support
- Email action support (mark as read, archive, delete)
- Custom summary templates
- Different AI models support (GPT, Claude, etc.)

### Improvements

- Better error handling and recovery
- Performance optimizations
- Improved logging and monitoring
- Better test coverage
- Docker multi-stage builds
- Kubernetes deployment manifests
- CI/CD pipeline setup

### Documentation

- Video tutorials
- More Home Assistant automation examples
- Deployment guides for different platforms
- Troubleshooting guides
- API documentation
- Architecture diagrams

### Bug Fixes

- Check [existing issues](https://github.com/murphy360/gmail_summaries/issues)
- Fix and submit a PR with description and tests

## Questions?

- Open a [GitHub Discussion](https://github.com/murphy360/gmail_summaries/discussions)
- Check existing documentation
- Contact the maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
