# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcommon.h

FreeType internal symbol-renaming header.

Key points:
- When `TT_PREFIX_ALL_NAMES` is defined, maps many internal names to `FT*`-prefixed equivalents.
- Covers modules such as:
  - `ttcalc`
  - lists/cache/error/mutex
  - raster
  - cmap
  - object/context/instance/face/glyph handling
  - TrueType table loading
  - glyph loading
  - interpreter
  - extensions
  - kerning
- Does not rename external `TT_` API functions.

Dependencies and interactions:
- Helps avoid link-time collisions when multiple FreeType-derived components or libraries are present.

Research relevance:
- Namespacing compatibility layer for embedded FreeType-derived code.
