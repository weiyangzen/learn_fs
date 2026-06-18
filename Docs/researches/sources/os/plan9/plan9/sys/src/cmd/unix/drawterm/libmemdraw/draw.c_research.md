# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/draw.c

Core in-memory draw engine for Plan 9 image compositing.

Main responsibilities:
- Initializes global solid images (`memwhite`, `memblack`, `memopaque`, `memtransparent`) in `_memimageinit`.
- Clips and normalizes draw parameters in `_memimagedrawsetup` and `drawclip`.
- Dispatches draw operations through `_memimagedraw`: hardware hook, optimized memory paths, character drawing, then general alpha compositing.
- Implements pixel readers/writers for sub-byte greyscale, CMAP8, byte-aligned RGB/alpha formats, and conversion buffers.
- Implements alpha and boolean Porter-Duff-style composition for Plan 9 draw operators.
- Provides fast paths for solid fills, same-channel copies, 1-bit boolean copies, and glyph masks.
- Converts between image pixel encodings and RGBA with `_imgtorgba`, `_rgbatoimg`, and `_pixelbits`.
- Provides `_memfillcolor`.

Important internal structures:
- `Memdrawparam`: draw setup contract shared by callers.
- `Buffer` and `Param`: scan-line channel buffers and reader/writer state.
- Precomputed bit replication/unpacking tables for 1/2/4-bit image depths.

Important behavior:
- Handles replicated sources/masks by coordinate wrapping and optional scan-line caching.
- Detects source/destination overlap and chooses reverse scan direction or buffering.
- Uses integer rounded division approximations for alpha math.
- Supports fallback-only hardware acceleration via `hwdraw`.
