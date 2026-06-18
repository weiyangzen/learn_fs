# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.h

Public declarations for line parameters and quality controls.

Key declarations:
- Standard PostScript line operators: linewidth, linecap, linejoin, miterlimit, dash, flatness, stroke adjust.
- Ghostscript extensions: dash adaptation, curve join, accurate curves, dot length, dot orientation.
- Imager-level accessors for flatness, dash adaptation, and accurate curves.

Dependencies:
- Includes `gslparam.h` for cap/join enum definitions.
- Forward-declares `gs_imager_state`.

Research notes:
- This header separates public graphics-state API from internal `gx_line_params` implementation details.
