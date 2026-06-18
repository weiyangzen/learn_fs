# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.h

## Purpose
Small header defining shared types for `ntfswipe.c`.

## Exports
- `enum action`:
  - `act_info`: calculate/report only.
  - `act_test`: execute no-action path.
  - `act_wipe`: perform writes.
- `struct options`: global command-line configuration consumed by `ntfswipe.c`.

## `struct options` Fields
- Device and logging/control: `device`, `info`, `force`, `quiet`, `verbose`, `noaction`.
- Overwrite control: `count`, `bytes`.
- Wipe selectors: `directory`, `logfile`, `mft`, `pagefile`, `tails`, `unused`, `unused_fast`, `undel`.

## Notes
- This header is implementation-specific rather than a general library API.
- It includes `types.h` and otherwise only provides state definitions used by the utility.
