# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcommon.h

Purpose: optional FreeType internal symbol-renaming header.

Key contents:
- When `TT_PREFIX_ALL_NAMES` is defined, maps many internal FreeType-style names to `FT*`-prefixed names.
- Covers arithmetic, list/cache/error/mutex/raster/cmap/object/loading/glyph/interpreter/debug/extension/kerning functions.
- Does not rename external `TT_` APIs.

Dependencies: none.

Integration notes: prevents link-time conflicts if multiple FreeType-derived components are linked together.

Risks: only active under `TT_PREFIX_ALL_NAMES`; mixed builds must use consistent macro settings.
