# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-base.h

## Role

Large inline helper header for initializing NVMe Base Specification admin commands and shared command dword fields. It centralizes bit shifts/masks and `struct libnvme_passthru_cmd` setup for many admin and common command families.

## Field Encoding

Defines `NVME_FIELD_ENCODE` if absent and enumerates command dword shifts/masks for:

- Get Log Page.
- Identify.
- Set/Get Features.
- Namespace Management and Attachment.
- Firmware Commit/Download.
- Directive Send/Receive.
- Device Self-test.
- Virtualization Management.
- Capacity Management.
- Lockdown.
- Format NVM.
- Security Send/Receive.
- Sanitize.
- Get LBA Status.
- I/O command set common fields.
- NVM DSM/reservation/copy fields.
- ZNS management fields.
- MI command flags.

## Major Helper Families

- Get Log initializers:
  - Generic `nvme_init_get_log()` and LPO helper.
  - Supported log pages, error, SMART, firmware slot, changed namespace, command effects, self-test, telemetry host/controller, endurance group, predictable latency, ANA, persistent event, LBA status, media unit status, capacity config list, FID effects, lockdown, boot partition, rotational media, dispersed namespace, management address list, power measurement, PHY RX EOM, reachability groups/associations, changed allocated namespaces, FDP config/RUH/stats/events, reservation, sanitize.
- Identify initializers:
  - Generic `nvme_init_identify()`.
  - Namespace/controller, active/allocated namespace lists, namespace descriptors, NVM set list, CSI namespace/controller/list forms, independent namespace identify, user data format, controller lists, primary/secondary controller capability/list, namespace granularity, UUID list, domain/endurance group lists, command set structure.
- Set Features initializers:
  - Generic `nvme_init_set_features()`.
  - Arbitration, power management, LBA range, temperature threshold, error recovery, volatile write cache, interrupt coalescing/config, write atomic, async events, APST, timestamp, HCTM, non-operational power state, read recovery level, predictable latency config/window, LBA status interval, host behavior, sanitize, endurance event config, software progress, host ID, reservation masks/persistence, write protect, I/O command set profile, live migration controller data queue.
- Get Features initializers:
  - Generic `nvme_init_get_features()`.
  - Mirrors many feature-specific set helpers and configures payload buffers where required.
- Namespace/firmware/admin command helpers:
  - Namespace create/delete, firmware commit/download, device self-test, namespace attach/detach, directive send/receive variants.
- Virtualization/live migration helpers:
  - Virtualization management, capacity management, discovery information management send, lockdown, live migration track send, migration send/receive, controller data queue create/delete.
- Security/sanitize/LBA status:
  - Format NVM, security send/receive, sanitize NVM, get LBA status, sanitize namespace.
- Utility:
  - `nvme_init_ctrl_list()` converts controller IDs to little endian in a controller list payload.

## Validation

Most helpers assume caller-supplied parameters are valid for the target command and only encode fields. Explicit validation exists in a few places:

- `nvme_init_fw_download()` rejects zero or non-dword-aligned lengths and non-dword-aligned offsets.
- `nvme_init_directive_recv_stream_status()` rejects `nr_entries > NVME_STREAM_ID_MAX`.

## Dependencies

Includes `errno.h`, `string.h`, `nvme/endian.h`, `nvme/ioctl.h`, `nvme/nvme-types-base.h`, and `nvme/nvme-types-nvm.h`.

## Notes

This header is the foundational command-construction layer used by other command-set headers. It does not submit commands; it only initializes passthrough command structures and payload helper structures.
