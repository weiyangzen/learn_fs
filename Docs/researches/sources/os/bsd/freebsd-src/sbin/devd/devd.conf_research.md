# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.conf

## Purpose
Default main `devd` configuration.

## Main Elements
- Options add `/etc/devd` and `/usr/local/etc/devd`, set pidfile, and define `wifi-driver-regex`.
- Network rules run `/etc/pccard_ether` on IFNET attach and wireless driver attach/detach.
- Example override for `ed50`.
- ACPI thermal warning and suspend/resume rc hooks.
- Large commented example block for ACPI, RCTL, coredumps, and DEVFS tty creation.

## Dependencies And Integration
Parsed first by `devd`, then extra directories are scanned. Establishes base event behavior and variables used by later rules.
