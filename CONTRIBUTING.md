
markdown
Copy
# Contribution Guidelines for Decentralized AGI Child

We welcome contributors of all skill levels! Follow these guidelines to ensure smooth collaboration.

## Table of Contents
1. [Before You Start](#before-you-start)
2. [Quick Contribution Steps](#quick-contribution-steps)
3. [Code Standards](#code-standards)
4. [Security Practices](#security-practices)
5. [Issue Labels](#issue-labels)
6. [Communication](#communication)
7. [License](#license)

---

## Before You Start
1. **Read** our [Architecture RFC](docs/ARCHITECTURE.md)
2. **Setup**:
   ```bash
   git clone https://github.com/Personaz1/decentralized-ai-child
   pip install -r requirements-dev.txt  # Includes testing/formatting tools
Join our Discord for real-time discussions.

Quick Contribution Steps
1. Find an Issue
First-time? Look for good first issue labels.

Advanced: Check priority/P0 for critical tasks.

2. Branch Naming
bash
Copy
git checkout -b type/description
# Examples:
# feature/p2p-discovery
# fix/security-audit-log
3. Development Flow
Test:

bash
Copy
pytest tests/ --cov=core  # Minimum 80% coverage required
Format:

bash
Copy
black . && ruff check --fix . && mypy core/
Document: Update relevant .md files if APIs change.

4. Submit Pull Request
Template:

markdown
Copy
## Changes
- [ ] Fixes #issue-number
- [ ] Breaking changes? (Explain migration path if yes)

## Validation
- [ ] Ran `pytest tests/ -v`
- [ ] Manual test steps: [e.g., "Tested DHT discovery with 10 nodes"]
Code Standards
Python:

Type hints for all functions/methods

Google-style docstrings

python
Copy
def federated_average(updates: list[ModelWeights]) -> ModelWeights:
    """Aggregate model updates from distributed nodes.
    
    Args:
        updates: List of model weight deltas from clients
        
    Returns:
        Global model weights after averaging
    """
Security:

All crypto must use audited libraries (libsodium, OpenSSL)

No raw eval() or pickle usage

Security Practices
Vulnerability Reports: @personaz1 TG

Audits: Cryptographic code requires 2 maintainer approvals

Secrets: Never commit API keys/credentials (use .env template)

Issue Labels
Label	Purpose
good first issue	Simple tasks for newcomers (e.g., docs, basic tests)
priority/P0	Showstoppers (network failures, security holes)
needs-design	Requires RFC proposal in Discussions
awaiting-review	PR needs maintainer attention
Communication
Discord: For real-time chat (channels: #p2p-dev, #ethics-review)

GitHub Discussions: For technical debates (use [RFC] prefix)

Weekly Sync: Every Friday 14:00 UTC (calendar in Discord)

License
By contributing, you agree to license your work under the AGPLv3 License. All derivative works must remain open-source.


 @personaz1 TG

---

### Key Features of This CONTRIBUTING.md:
1. **Onboarding Flow**: Clear path from setup to first PR
2. **Security-First**: PGP/PKI-ready template
3. **Quality Control**: Enforces testing/formatting pre-commit
4. **Community Building**: Links to Discord/Discussions
5. **License Clarity**: AGPLv3 compliance emphasized

Add this to your repo's root, and contributors will have everything they need to start collaborating effectively!
