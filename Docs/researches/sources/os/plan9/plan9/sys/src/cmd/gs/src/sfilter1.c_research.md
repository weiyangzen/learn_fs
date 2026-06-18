# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter1.c

Level 1 simple Ghostscript filters: `PFBDecode` and `SubFileDecode`.

Key behavior:
- `PFBDecode` parses binary Type 1 PFB records beginning with `0x80`, accepts text, binary, and EOF record types, converts text record CR to LF, and can convert binary records to hex when `binary_to_hex` is set.
- PFB record lengths are read as little-endian 32-bit values; invalid record markers return `ERRC`, EOF record returns `EOFC`.
- `SubFileDecode` can either copy a fixed number of bytes without an EOD pattern or scan for an EOD byte pattern.
- SubFileDecode supports `skip_count`, repeated EOD counting, partial EOD matches across buffer boundaries, and delayed copying of bytes that looked like a partial EOD but did not complete.

Notable dependencies:
- `sfilter.h` for state definitions.
- `strimpl.h` stream cursor/template machinery.

Research notes:
- SubFileDecode’s pattern fallback can be quadratic in EOD length, explicitly accepted because EOD strings are expected to be small.
- PFBDecode returns partial progress cleanly when headers or records span buffers.
