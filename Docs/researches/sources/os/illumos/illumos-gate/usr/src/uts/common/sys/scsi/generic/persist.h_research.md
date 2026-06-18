# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/persist.h

This header defines SCSI persistent reservation command constants and wire-format structures for Persistent Reserve In/Out and related TransportID data.

Key definitions:
- Defines Persistent Reserve In service actions: read keys, read reservation, report capabilities, and read full status.
- Defines persistent reservation scope and type codes.
- Defines Persistent Reserve Out service actions: register, reserve, release, clear, preempt, preempt-abort, register-and-ignore-existing-key, and register-move.
- Defines TransportID sizes and protocol-related constants for FC, SPI, SBP, SRP, and iSCSI.
- Defines endian-variant structures for:
  - PR IN CDB
  - read reservation/key response descriptors
  - reservation type capability bits
  - report capabilities response
  - generic/FC/iSCSI/SRP TransportID forms
  - read full status descriptors
  - PR OUT CDB
  - PR OUT parameter lists
  - register-and-move parameter list

Dependencies:
- Uses standard integer types and bitfield order macros from the surrounding illumos environment.

Impact:
- Used by storage stack components implementing reservations, clustering, fencing, and multipath coordination.

Cautions:
- Many structures use trailing single-element arrays for variable-length payloads.
- Multi-byte fields are wire-format byte arrays rather than host-order integers in many structures.
- Correct bitfield interpretation depends on `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
