# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/bit.c

Small helper module for ATA diagnostic bit/table formatting and little-endian accessors.

Important behavior:
- `sebtab` appends names for set bits into a buffer.
- `pw`, `pdw`, and `pqw` store 16/32/64-bit little-endian values.
- `w`, `dw`, and `qw` read little-endian values.

Used by `atazz/main.c` and SCT/table command construction.
