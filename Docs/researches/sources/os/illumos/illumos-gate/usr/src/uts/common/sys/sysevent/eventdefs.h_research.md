# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/eventdefs.h

## Purpose
Central registry of public sysevent class and subclass string constants.

## Main Interfaces
- Generic/internal classes: `EC_NONE`, `EC_PRIV`.
- Hardware/platform classes including DR, domain, environment, IPMP, device, fault management, platform, power control, ACPI, ZFS, datalink, VRRP, and PCIe.
- Subclass constants for:
  - DR attachment point, request, and target-state changes.
  - Domain state/loghost changes.
  - IPMP group, interface, member, and probe changes.
  - Device add/remove/branch/DLE/eject events.
  - FMA errors and replays.
  - Power control and ACPI events.
  - ZFS pool, vdev, scrub, resilver, trim, config, and history events.
  - Datalink link state, VRRP state change, and PCIe link state.

## Dependencies And Relationships
Included by schema-specific headers such as `sysevent/dev.h` and by event producers/consumers that need the canonical class/subclass strings.

## Research Notes
This file is a compatibility boundary. The string values are the event taxonomy visible to userland listeners and administrative tooling.
