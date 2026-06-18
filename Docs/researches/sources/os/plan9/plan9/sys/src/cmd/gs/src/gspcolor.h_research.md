# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.h

Defines the client interface for Pattern colors.

Key definitions:
- `gs_pattern_type_t` forward declaration.
- `gs_pattern_template_common` and `gs_pattern_template_t`.
- Pattern template GC descriptor macros.
- `gs_pattern_instance_t` with `rc_header`, pattern type, saved graphics state, and pattern ID.
- Pattern instance GC descriptor macros.

Exports:
- `gs_setpattern`
- `gs_setpatternspace`
- `gs_make_pattern`
- `gs_get_pattern`
- `gs_pattern_reference`

Integration:
- Includes `gsccolor.h`, `gsrefct.h`, and `gsuid.h`.
- Provides common base for `gsptype1.h` and `gsptype2.h`.

Risk notes:
- Pattern instances are reference-counted and retain saved graphics state; clients holding colors outside the graphics state must call `gs_pattern_reference` correctly.
