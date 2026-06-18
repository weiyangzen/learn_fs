# File Research: sources/os/bsd/freebsd-src/sbin/devd/devmatch.conf

## Purpose
Connects `devd` NOMATCH events to the `devmatch` service.

## Main Elements
- High-priority ignores for events lacking useful location/PNP data.
- Ignores ACPI `_HID=none`.
- Generic `nomatch 100` action runs `service devmatch quietstart $*`.
- Comments document how to override with higher-priority no-op rules or rc.conf.

## Dependencies And Integration
Works with `devmatch(8)` and kernel NOMATCH event strings.
