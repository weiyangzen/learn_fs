# File Research: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.c

Read completely: 275 lines, 8008 bytes.

DWB pathname initialization helper for troff/nroff. It calculates the DWB home directory from environment/defaults, optionally reads debug configuration, and rewrites path pointer/array entries listed in `dwbinit` arrays.

Key behavior:
- `DWBhome` determines the active DWB root, using `DWBHOME` and defaults.
- `DWBdebug` emits path-debug information controlled by `DWBDEBUG`.
- `DWBinit` walks `dwbinit` entries, prefixes relative paths with the DWB home, preserves absolute paths, allocates replacement strings for pointer entries, and copies into bounded arrays where possible.
- Supports `\*(.P` prefix semantics for DWB-relative paths.

Dependencies:
- Includes `tdef.h` and `dwbinit.h`; used by `n1.c` for `DWBfontdir`, `DWBntermdir`, `DWBalthyphens`, `DWBhomedir`, and `nextf`.

Reliability notes:
- Bounded array entries are checked for room.
- Pointer entries are reallocated and can fatal-error on allocation failure.
