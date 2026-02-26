# AGENTS.md

## Cursor Cloud specific instructions

### Overview

ELISA-FEDERAL is a Python 3.9+ CLI tool for security analysis of public websites. It has no databases, no Docker, no web frontend, and no external API keys.

### Running the application

```bash
python3 elisa.py --help          # Show help
python3 elisa.py --version       # Show version
python3 elisa.py scan <URL> --quick   # Quick scan
python3 elisa.py scan <URL>           # Basic scan
python3 elisa.py scan <URL> --full    # Full scan
python3 elisa.py monitor <URL>        # Continuous monitoring (blocks; Ctrl+C to stop)
```

A target URL (any public website, e.g. `https://www.gov.br`) is required for scan/monitor commands. Reports are saved to `reports/` in Markdown and JSON formats.

### Configuration

Copy `config/settings.example.json` to `config/settings.json` before first use. Directories `logs/`, `reports/`, `cache/`, `temp/` are auto-created by the application.

### Known caveats

- The `report --list` and `report --view` subcommands shown in README are **not wired** into the argparse CLI; invoking them will produce an "unrecognized arguments" error. This is a pre-existing limitation.
- There is no automated test suite or linter configuration in the repository. Validation is done by running the CLI commands directly.
- The `install.sh` script is interactive (prompts for venv creation) and should not be used in non-interactive environments. Use `pip install -r requirements.txt` directly instead.
