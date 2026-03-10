# Changelog

All notable changes to SnortAMV will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2026-03-11

### Added
- Enhanced configuration validation with comprehensive checks on Snort configuration files
- Better error messages throughout the application for improved user experience

### Fixed
- Fixed circular import issue in `version.py` that could cause CLI version display problems
- Corrected path handling in configuration validation for cross-platform compatibility
- Resolved issue where empty rule files were not properly detected during validation

### Changed
- Refactored validation logic in `modules/configuration/validate_conf.py` for better maintainability
- Updated inline comments and docstrings in configuration modules

### Technical
- Modified `modules/configuration/validate_conf.py` to include more robust validation checks
- Updated version handling to prevent import cycles

## [0.0.1] - 2026-01-01

### Added
- Initial release of SnortAMV - Automated Snort IDS Manager
- Account management system with SQLite backend
- Rule management with enable/disable functionality
- Cross-platform support (Windows, Linux distributions, macOS)
- TLS traffic decryption capabilities
- Automated Snort installation for various OS package managers
- CLI interface with comprehensive commands
- Configuration validation and setup tools