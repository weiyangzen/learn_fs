# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp.c

## Role

Defines System Use Sharing Protocol signature tables and handlers for HSFS, plus the extension registry that enables RRIP parsing.

## Main Behavior

- Defines `susp_signature_table` mapping common SUSP signatures:
  - `SP` to `share_protocol()`
  - `CE` to `share_continue()`
  - `PD` to `share_padding()`
  - `ER` to `share_ext_ref()`
  - `ST` to `share_stop()`
- Exposes `susp_sp` and `susp_ce` as stable pointers to the first two table entries.
- Defines `extension_name_table` with SUSP first and RRIP second; the order matters because RRIP bit position is assumed by RRIP macros.

## Handlers

- `share_protocol()` validates SUSP check bytes, verifies supported version, sets the SUSP implemented bit, and records the SUA offset.
- `share_ext_ref()` scans known extension names and sets implemented bits for matching extension references.
- `share_continue()` records continuation area LBN, offset, and length for later reading.
- `share_padding()` skips padding records.
- `share_stop()` marks end of SUA parsing.

## Dependencies And Interactions

- Used by `parse_sua()` and `hs_check_root_dirent()` in `hsfs_susp_subr.c`.
- Enables RRIP handlers from `hsfs_rrip.c` after `ER` records are recognized.
