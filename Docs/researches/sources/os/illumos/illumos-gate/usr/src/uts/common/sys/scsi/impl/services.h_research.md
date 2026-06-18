# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/services.h

This header declares implementation services for SCSI polling, packet allocation, name decoding, error reporting, logging, capability string tables, and interconnect type constants.

Key definitions:
- Defines `scsi_key_strings` and `scsi_asq_key_strings` lookup table structures.
- Declares packet helpers `scsi_poll()`, `get_pktiopb()`, and `free_pktiopb()`.
- Declares string/decoder helpers for device type, completion reason, message, command, sense key, extended sense key, and ASC/ASCQ.
- Declares generic and vendor-unique SCSI error message functions.
- Declares `scsi_log()` with printf-like checking.
- Declares global `scsi_state_bits` and `sense_keys`.
- Defines SCSI error severity constants.
- Defines SCSI capability indexes and `SCSI_CAP_ASCII`.
- Defines SCSI version constants.
- Defines interconnect type constants and strings for SPI, Fibre, 1394, SSA, fabric, USB, ATAPI, iSCSI, IB/SRP, SATA, and SAS.
- Defines compatibility alias `scsi_cmd_decode`.

Dependencies:
- Kernel-only content is gated by `_KERNEL`.
- Depends on sense-key counts from the sense headers and SCSA packet/device types from the include context.

Impact:
- This is the common diagnostics and capability support surface for SCSI framework and drivers.

Cautions:
- Capability arrays are index-sensitive; additions must update indexes, ASCII mapping, and maximum values consistently.
- Error reporting APIs accept driver-supplied command/ASC tables and FRU decoders, so callers control part of diagnostic interpretation.
