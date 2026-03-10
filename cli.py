#!/usr/bin/env python3
import os, time, pyfiglet, shutil, platform, subprocess, sys, argparse
from pathlib import Path
from rich.console import Console
from modules.configuration.setup_rules import create_default_rules, interactive_add_rule
from modules.configuration.validate_conf import validate_configuration
from modules.acc_managt.creat_acc import create_account_cli
from modules.acc_managt.delete_acc import delete_account_cli
from modules.acc_managt.update_acc import update_account_cli
from modules.utilities.logger import get_logger
from modules.utilities.error_handler import get_error_logger
from modules.configuration.rule_manager import (
    disable_rule,
    enable_rule,
    list_rules,
    build_ruleset,
    backup_rules,
)


ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

console = Console()
OS_TYPE = platform.system().lower()
VERSION = "0.0.1"

logger = get_logger(__name__)
logerror = get_error_logger(__name__)
clierrorlogger = get_error_logger("cli")

# -------------------- Helper Functions --------------------
def get_linux_distro():
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return None

    data = {}
    for line in os_release.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k] = v.strip('"')

    return {
        "id": data.get("ID"),
        "name": data.get("NAME"),
        "version": data.get("VERSION_ID"),
    }


def distro_detector():
    distro = get_linux_distro()
    if OS_TYPE == "linux":
        if not distro:
            print(" Cannot detect Linux distro")
            sys.exit(1)
        print(f"Running on {distro['name']} {distro['version']}")
    else:
        return


def get_pkg_manager(distro):
    distro_id = distro["id"]

    if distro_id in ("ubuntu", "debian"):
        return "apt"
    if distro_id in ("fedora", "rhel", "centos"):
        return "dnf"
    if distro_id in ("arch", "manjaro"):
        return "pacman"

    return None


# ---------------- UI ----------------
def greeting_by_time():
    hour = int(time.strftime("%H"))
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    elif hour < 21:
        return "Good Evening"
    return "Good Night"


def banner():
    console.print(pyfiglet.figlet_format("SNORT AMV"), style="bold green")
    console.print(f"{greeting_by_time()} 👋", style="green")


# ---------------- Core ----------------
def check_snort():
    snort_path = shutil.which("snort") or shutil.which("snort3")
    if not snort_path:
        logger.warning("Snort not detected")
    return snort_path


def setup_cmd(_):
    if OS_TYPE == "linux":
        try:
            result = subprocess.run([sys.executable, "post_installer.py"], check=True)
            if result.returncode != 0:
                logerror.exception("Post installation failed: %s", result.stderr)
            else:
                logger.info("Post installation completed successfully")
        except Exception as e:
            logerror.exception("Error during post installation: %s", e)
    elif OS_TYPE == "windows":
        try:
            result = subprocess.run([sys.executable, "post_installer.py"], check=True)
            if result.returncode != 0:
                logerror.exception("Post installation failed: %s", result.stderr)
            else:
                logger.info("Post installation completed successfully")
        except Exception as e:
            logerror.exception("Error during post installation: %s", e)
    else:
        logger.error("Unsupported OS for setup")
        return


def run_cmd(_):
    if OS_TYPE == "linux":
        try:
            subprocess.run(["bash", "snort_auto.bash"], check=True)
        except subprocess.CalledProcessError as e:
            logerror.exception("Snort run failed: %s", e)
            logerror.exception("Stdout: %s", e.stdout)
            logerror.exception("Stderr: %s", e.stderr)
            return
    elif OS_TYPE == "windows":
        try:
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", "snort.ps1"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logerror.exception("Snort run failed: %s", e)
            logerror.exception("Stdout: %s", e.stdout)
            logerror.exception("Stderr: %s", e.stderr)
            return
    else:
        sys.exit("Unsupported OS")


def decrypt_cmd(_):
    if OS_TYPE == "linux":
        cmd = ["bash", "decrypt.bash"]
    elif OS_TYPE == "windows":
        cmd = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "decrypt.ps1",
        ]
    else:
        logger.error("Unsupported OS")
        return

    logger.info("Starting decryption process")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error("Decryption failed")
        logerror.exception("STDOUT:\n%s", result.stdout)
        logerror.exception("STDERR:\n%s", result.stderr)
        print("[❌] Decryption failed. Check logs for details.")
        return

    logger.info("Decryption completed successfully")
    print("[✅] Decryption completed successfully")


def version_cmd(_):
    print(f"SnortAMV v{VERSION}")


def create_acc(_):
    from modules.acc_managt.migrate import migrate_acc

    try:
        # Creates the account
        create_account_cli(ROOT)
        #  migrates the account to the database
        migrate_acc()
        logger.info("Account Created successfully")
    except Exception as e:
        logerror.exception("Any error occured while creating account: %s", e)


def rule_enable_cmd(args):
    enable_rule(args.name, path=args.path, dry_run=args.dry_run)


def rule_disable_cmd(args):
    disable_rule(args.name, dry_run=args.dry_run)


def rule_build_cmd(args):
    build_ruleset(dry_run=args.dry_run)


# ---------------- CLI ----------------
def main():
    try:
        banner()

        parser = argparse.ArgumentParser(description="SnortAMV – Automated Snort Manager")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate actions without making changes",
        )
        sub = parser.add_subparsers(dest="command", required=True)

        sub.add_parser("setup", help="Run initial setup").set_defaults(func=setup_cmd)
        sub.add_parser("run", help="Runs the snort").set_defaults(func=run_cmd)
        sub.add_parser("decrypt", help="decrypt the snort to be readable").set_defaults(
            func=decrypt_cmd
        )
        sub.add_parser("--validate-conf", help="Validate the configuration").set_defaults(
            func=lambda _: validate_configuration(ROOT)
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"SnortAMV v{VERSION}",
        )

        rule = sub.add_parser("rule", help="add an list out rules")
        rule_sub = rule.add_subparsers(dest="action", required=True)
        rule_sub.add_parser("add", help="Create a local rule interactively").set_defaults(
            func=lambda _: interactive_add_rule(ROOT)
        )
        rule_sub.add_parser("list", help="List rules").set_defaults(
            func=lambda _: list_rules()
        )
        enable = rule_sub.add_parser("enable", help="Enable a rule")
        enable.add_argument("name", help="Name of the rule to enable")
        enable.add_argument(
            "--from",
            dest="path",
            choices=["sources", "disabled"],
            required=True,
            help="Where to enable the rule from",
        )
        enable.set_defaults(func=rule_enable_cmd)

        disable = rule_sub.add_parser("disable", help="Disable a rule")
        disable.add_argument("name", help="Name of the rule to disable")
        disable.set_defaults(func=rule_disable_cmd)

        rule_sub.add_parser("build", help="Build up the rules").set_defaults(
            func=rule_build_cmd
        )
        rule_sub.add_parser("backup", help="List local.rules").set_defaults(
            func=lambda _: backup_rules()
        )

        acc = sub.add_parser(
            "acc", help="Create, Delete and update project profile or users"
        )
        acc_sub = acc.add_subparsers(dest="action", required=True)
        acc_sub.add_parser("create", help="Create a project user").set_defaults(
            func=create_acc
        )
        acc_sub.add_parser("delete", help="Delete a project user").set_defaults(
            func=lambda _: delete_account_cli(ROOT)
        )
        acc_sub.add_parser("update", help="Update a project user").set_defaults(
            func=lambda _: update_account_cli(ROOT)
        )

        args = parser.parse_args()
        if args.dry_run:
            console.print(
                "[⚠️] Dry-run mode enabled: No changes will be made to the system.",
                style="yellow",
            )
        args.func(args)
    except KeyboardInterrupt:
        logger.info("Altered by The user")
    except Exception as e:
        clierrorlogger.exception("cli Fatal crash from the cli")
        return "[bad] Fatal error occurred. Check logs."


if __name__ == "__main__":
    main()
