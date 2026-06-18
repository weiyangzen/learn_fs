# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/camcontrol.h

## Purpose
Shared declarations and enums for `camcontrol` command modules.

## Main Elements
- Defines option lookup result enum `camcontrol_optret`.
- Defines device type enum `camcontrol_devtype` covering SCSI, SATL, ATA, NVMe, MMCSD, unknown, and none.
- Declares `struct get_hook` for argument callback helpers.
- Declares global `verbose`.
- Declares ATA, SCSI, firmware, zone, EPC, timestamp, depop, mode, inquiry, persistent reservation, attribute, argument, confirmation, and usage helper APIs.

## Dependencies And Integration
Included across `camcontrol` modules. It is the local interface contract between command parser/core and subcommand implementations.

## Risk Notes
Prototype changes here affect many storage command modules.
