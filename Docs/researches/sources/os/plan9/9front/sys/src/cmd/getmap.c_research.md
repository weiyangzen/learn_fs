# File Research: sources/os/plan9/9front/sys/src/cmd/getmap.c

Plan 9 colormap loader/applicator for 8-bit draw displays.

Key responsibilities:
- Reads colormaps from explicit files, `/lib/cmap/`, display colormap files, or generated gamma maps.
- Supports `gamma`, `gammaN`, `rgamma`, and `rgammaN` generated grayscale maps.
- Validates 256-line colormap files with index plus RGB fields.
- Writes the selected colormap to `/dev/draw/<id>/colormap`.

Important behavior:
- Opens `/dev/draw/new`, extracts the display id, and only proceeds for `m8` CMAP8 displays.
- `rep()` replicates an n-bit value across a 32-bit word but is not used by `main()`.

Notable risks:
- Allocated read buffers are not freed, but the command is short-lived.
- The fallback comparison for `screen`/`display`/`vga` checks the composed `name`, not the original argument after directory probing.
