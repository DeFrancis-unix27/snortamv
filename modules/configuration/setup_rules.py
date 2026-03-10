"""Create and manage local.rules inside the project (simple rule format)."""

from pathlib import Path
from rich.console import Console
from modules.utilities.logger import get_logger
from modules.utilities.error_handler import get_error_logger

errorlog = get_error_logger(__name__)

logger = get_logger(__name__)
console = Console()

DEFAULT_RULES = [
    'alert icmp any any -> any any (msg:"ICMP detected"; sid:1000001; rev:1;)\n',
]


def create_default_rules(root: Path):
    rules_dir = root / "rules"
    rules_dir.mkdir(exist_ok=True)
    local_rules = rules_dir / "generated" / "snort.rules"
    if not local_rules.exists():
        local_rules.parent.mkdir(exist_ok=True)
        local_rules.write_text("".join(DEFAULT_RULES))
        console.print(f"Created default local.rules at {local_rules}", style="green")
    else:
        console.print("local.rules already exists", style="yellow")


def interactive_add_rule(root: Path):
    rules_dir = root / "rules"
    rules_dir.mkdir(exist_ok=True)
    filename = input(
        "What name do want to give to your new rules file (without .rules extension): \n"
    ).strip()
    local_rules = rules_dir / "sources" / f"{filename}.rules"

    # Create file with default rules only once
    if not local_rules.exists():
        local_rules.parent.mkdir(exist_ok=True)
        local_rules.write_text("")
        console.print("\t local.rules created with default rules.", style="green")

    # Show existing rules
    console.print("\nCurrent rules:\n", style="blue")
    for rules in DEFAULT_RULES:
            console.print(f" Example of how rules are written \n {rules}", style="purple")
    console.print(local_rules.read_text(), style="green")

    print("\n Add a simple alert rule (demo)")

    # --- User input -----------------------------------------------------------
    proto = input("Protocol (tcp/udp/icmp/ip): ").strip().lower()
    if proto not in {"tcp", "udp", "icmp", "ip"}:
        print("Invalid protocol.")
        return

    src = input("Source (e.g. 192.168.0.2 or any): ").strip()
    src_port = input("Source port (e.g. 80 or any): ").strip()
    dst = input("Destination (e.g. 192.168.0.10 or any): ").strip()
    dst_port = input("Destination port (e.g. 443 or any): ").strip()
    msg = input("Message: ").strip()

    try:
        sid = int(input("SID (unique integer e.g. 1000001 ): "))
        rev = int(input("Rev (integer e.g. 1): "))
    except ValueError:
        print("SID and Rev must be integers.")
        return

    # --- Build rule -----------------------------------------------------------
    rule = (
        f"alert {proto} {src} {src_port} -> {dst} {dst_port} "
        f'(msg:"{msg}"; sid:{sid}; rev:{rev};)\n'
    )

    # Append rule safely
    with open(local_rules, "a") as f:
        f.write(rule)

    print(f"\n Rule successfully added to {local_rules}")
    logger.info("Rule successfully added to {local_rules}")

def list_local_rules(root: Path):
    local_rules = root / "rules" / "local.rules"
    if not local_rules.exists():
        print("No local.rules found. Run `python main.py setup` to create defaults.")
        logger.info("No local.rules found. Run `python main.py setup` to create defaults.")
        return
    print(local_rules.read_text())
