# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.h

Client interface for Ghostscript character rendering/show operations.

Key contents:
- Includes `gsccode.h` and `gscpm.h`.
- Forward-declares opaque `gs_show_enum` and `gs_font`.
- Declares show enumerator allocation/release:
  - `gs_show_enum_alloc`
  - `gs_show_enum_release`
- Declares text initialization APIs for show, ashow, widthshow, awidthshow, kshow, xyshow, glyphshow, cshow, stringwidth, charpath, glyphpath, glyphwidth, and charboxpath.
- Declares `gs_show_use_glyph`.
- Defines continuation result aliases:
  - `gs_show_render`
  - `gs_show_kern`
  - `gs_show_move`
- Declares enumeration/accessors:
  - `gs_show_next`
  - current/previous/next char accessors
  - current font/glyph
  - current and cumulative width
  - charpath mode
  - width-only query
- Declares cache/metric operators:
  - `gs_setcachedevice_float`
  - `gs_setcachedevice_double`
  - `gs_setcachedevice`
  - `gs_setcachedevice2_float`
  - `gs_setcachedevice2_double`
  - `gs_setcachedevice2`
  - `gs_setcharwidth`

Important implementation notes:
- The API exposes text rendering as an enumerator/coroutine-style protocol: initialize, repeatedly call `gs_show_next`, respond to positive continuation codes, and stop on zero or negative.
- Macros map default `gs_setcachedevice` and `gs_setcachedevice2` to float variants for compatibility.
