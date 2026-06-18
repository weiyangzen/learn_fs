# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharout.c

This file contains common outline-font character output helpers used by Type 1, Type 4, Type 42, and CID font paths.

Key behavior:
- `zchar_exec_char_proc` executes a PostScript outline procedure inside `systemdict` and font dictionary scopes.
- `zchar_get_metrics` reads Metrics entries and supports width-only, 2-element, and 4-element side-bearing/width formats.
- `zchar_get_metrics2` reads vertical Metrics2 entries.
- `zchar_get_CDevProc` detects a font CDevProc.
- `zchar_set_cache` combines width, bbox, Metrics2, default vertical metrics, CDevProc, and width-only short-circuiting into `setcachedevice`/`setcachedevice2` behavior.
- `zchar_charstring_data` fetches CharStrings data and special-cases a common `.notdef` procedure into a synthetic Type 1 charstring.
- `zchar_enumerate_glyph` iterates CharStrings dictionary keys and maps integer keys to CID glyphs or name keys to glyph names.

Important dependencies:
- Uses `gscrypt1.h` to synthesize encrypted `.notdef` charstrings when needed.
- Uses common show/cache APIs from `ichar.h` and `icharout.h`.

Research notes:
- This is shared glue between font dictionaries and lower-level glyph cache/rendering code.
- It is compatibility-heavy, especially around Metrics/CDevProc and malformed `.notdef` entries.
