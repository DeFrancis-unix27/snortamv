from pathlib import Path


def validate_configuration(root: Path):
    # Simple validation: check that rules file exists and is not empty
    rules = root / "rules" / "generated"/"snort.rules"
    if not rules.exists():
        print("Validation failed: snort.rules missing")
        return False
    content = rules.read_text().strip()
    if not content:
        print("Validation failed: snort.rules is empty")
        return False
    print("Configuration validation: ok (demo)")
    return True
