# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrect.c

## Purpose
Implements rectangle-oriented command-list writing for fills, tiles, mono/color/alpha copies, and RasterOp strip copies. It converts device drawing calls into compact command opcodes and payloads.

## Public Surface
- `cmd_write_rect_cmd(...)`: emits a rectangle command using compact full, short, tiny, or delta encodings.
- Device procedures: `clist_fill_rectangle`, `clist_strip_tile_rectangle`, `clist_copy_mono`, `clist_copy_color`, `clist_copy_alpha`, and `clist_strip_copy_rop`.

## Implementation
- Tracks prior rectangle state and writes small deltas when possible, falling back to full variable-length rectangle coordinates.
- Fill and tile rectangle procedures update color/tile state, disable incompatible logical operations when needed, and emit rectangle commands per affected band.
- Mono/color/alpha copy procedures compress bitmap payloads with allowed compression modes and split transfers by height or row width when a single command would exceed limits.
- Tile and RasterOp handling caches tile ids, writes tile color and phase changes, and may synthesize ids for anonymous texture tiles.
- `clist_strip_copy_rop` estimates colors used, marks slow RasterOps for render-plane decisions, writes texture tile state, enables the logical operation, then delegates to fill/copy commands while suppressing their normal RasterOp disabling.

## Dependencies
Uses clist command/state macros, bitmap compression helpers from other clist files, RasterOp tables/macros, tile cache helpers, and Ghostscript device procedures.

## Risks and Notes
- Some oversized tile cases are handled by scanline subdivision; shifted multi-line tile fallback is explicitly not handled.
- The CMYK RasterOp path includes a hack that treats 4-component devices as subtractive and flags slow ROPs for full-pixel rendering.
- `copy_alpha` returns an unknown error when the target disables non-1-bit alpha copy support.

Filesystem relevance: none directly. This is command serialization for banded rendering.
