# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.h

Header for DWB pathname initialization.

Key contents:
- Defines `dwbinit`, which describes either a pointer pathname or a fixed-size array pathname.
- Declares `DWBinit()`, `DWBhome()`, and `DWBprefix()`.

Important behavior:
- For pointer entries, `address` is set and `value` is null.
- For array entries, `value` is set and `length` must be the array capacity.
- The list is terminated by an entry with both `address` and `value` null.
