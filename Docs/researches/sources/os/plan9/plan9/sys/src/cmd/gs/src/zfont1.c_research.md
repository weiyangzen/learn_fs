# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfont1.c

## Purpose
Builds Type 1 and Type 4 CharString fonts and provides shared CharString-font parameter parsing used by Type 2/CID font code.

## Key Functions
- `charstring_font_get_refs()` extracts `Private`, `OtherSubrs`, `Subrs`, and initializes `GlobalSubrs`.
- `charstring_font_params()` reads Type 1 private dictionary hinting and interpreter parameters.
- `charstring_font_init()` fills `gs_font_type1` data and installs glyph procedures.
- `build_charstring_font()` builds and defines Type 1-like fonts.
- `zbuildfont1()` and `zbuildfont4()` build Type 1 encrypted and Type 4 disk-based fonts.
- `z1_same_font()` compares outline, metrics, and encoding identity.

## Important Behavior
- Missing `OtherSubrs`/`Subrs` become empty arrays.
- Out-of-range `BlueScale` is clamped.
- Non-0/1 `LanguageGroup` values are normalized to 0 for compatibility.
- `same_font` comparisons inspect `CharStrings`, `Private`, metrics dictionaries, and `Encoding`.

## Research Notes
Shared base for CharString-based font families; `zfont2.c` adds Type 2-specific parameters.
