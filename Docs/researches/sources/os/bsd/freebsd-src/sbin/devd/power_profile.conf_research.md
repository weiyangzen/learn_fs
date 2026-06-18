# File Research: sources/os/bsd/freebsd-src/sbin/devd/power_profile.conf

## Purpose
Switches power profile on AC line state changes.

## Main Elements
- Matches ACPI `ACAD` notifications.
- Runs `service power_profile $notify`.

## Dependencies And Integration
Installed on i386, amd64, and arm64 in the ACPI package group.
