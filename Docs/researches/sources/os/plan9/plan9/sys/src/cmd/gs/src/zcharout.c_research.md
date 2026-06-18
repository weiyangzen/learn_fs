# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharout.c

Contains shared outline-font support for Type 1, Type 4, and Type 42 rendering.

Key behavior:
- `zchar_exec_char_proc` executes procedure-defined outlines inside `systemdict` and font dictionary `begin`/`end` wrappers.
- `zchar_get_metrics` reads `Metrics` entries, accepting width-only, `[sbx wx]`, and `[sbx sby wx wy]` forms.
- `zchar_get_metrics2` reads vertical `Metrics2` arrays.
- `zchar_get_CDevProc` detects a font `CDevProc`.
- `zchar_set_cache` computes cache device parameters, expands bbox for stroked fonts, applies Metrics2/default vertical metrics, and either calls `setcachedevice[2]` directly or schedules CDevProc/setcachedevice through the estack.
- `zchar_charstring_data` fetches glyph CharStrings and special-cases ADOBEPS4 `.notdef` procedures by synthesizing a minimal encrypted or unencrypted Type 1 CharString.
- `zchar_enumerate_glyph` enumerates glyph names or CID integers from a dictionary.

Dependencies and coupling:
- Provides the common cache and metrics layer used by `zchar1.c`, `zchar42.c`, and font embedding/outline code.
- Important for VM/GC safety because generated `.notdef` CharString data is allocated in font memory and attached to glyph data.
