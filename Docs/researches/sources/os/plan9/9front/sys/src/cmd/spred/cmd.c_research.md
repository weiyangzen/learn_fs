# File Research: sources/os/plan9/9front/sys/src/cmd/spred/cmd.c

`spred/cmd.c` implements textual commands for the `spred` sprite editor command window.

Key responsibilities:
- `dopal`: opens or creates a palette file/window.
- `dosize`: resizes the active palette or sprite, parsing `N` for palettes and `W*H` for sprites.
- `doset`: sets the selected palette color from a numeric RGB value.
- `dozoom`: changes active window zoom and redraws.
- `dospr`: opens or creates a sprite, reads its file if present, creates a sprite window, and loads referenced palette.
- `dowrite`: writes the active palette/sprite, optionally to a specified file.
- `doquit`: calls `quit` and exits all threads when no unsaved-change confirmation remains.
- `docmd`: tokenizes a command line, dispatches through the `cmds` table, checks arity, and prints `?` on errors.

Important interactions:
- Uses global `mc`, active file/window globals from `dat.h`, and file/window helpers from `fns.h`.
- Palette and sprite file formats are implemented in `pal.c` and `spr.c`.
