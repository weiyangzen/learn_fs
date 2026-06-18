# File Research: sources/os/bsd/freebsd-src/sbin/devd/asus.conf

## Purpose
Defines ASUS and ASUS-Eee ACPI hotkey event actions.

## Main Elements
- Matches ACPI ASUS notify codes for mute, volume down, and volume up.
- Provides commented examples for additional EeePC user hotkeys.

## Dependencies And Integration
Installed when ACPI support is enabled. Actions call `mixer`.
