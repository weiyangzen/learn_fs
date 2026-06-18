# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv.h

Shared declarations and macros for `tcs` converter modules.

Contents:
- Prototypes for Japanese, Big5, GB, GBK, KSC, HTML, and tune input/output converters.
- `emit(x)` macro appends a rune through a `Rune **r` cursor.
- `NRUNE` is `Runemax+1` for reverse lookup table sizing.
- Declares global `long tab[]` reverse mapping table indexed by rune.

Role:
- Lets format-specific converter modules share the same function signatures expected by the main `tcs` driver.
