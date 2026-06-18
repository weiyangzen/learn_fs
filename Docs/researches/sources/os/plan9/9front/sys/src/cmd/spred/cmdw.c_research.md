# File Research: sources/os/plan9/9front/sys/src/cmd/spred/cmdw.c

`spred/cmdw.c` implements the editable command/output window for `spred`.

Key responsibilities:
- Defines `cmdtab`, the `Wintab` implementation for command windows.
- Draws the command window frame and scrollbar with `cmddraw` and `scrollbar`.
- Scrolls by lines with `cmdscroll`.
- Handles mouse selection and right-button scrollbar behavior with `cmdclick` and `cmdrmb`.
- Inserts and deletes rune ranges with `cmdinsert` and `cmddel`.
- Maintains frame selection with `setsel`.
- Executes the current command line from `opoint` through `cmdline` and `docmd`.
- Handles keyboard input in `cmdkey`, including view/up/left/right, deletion, newline command execution, and text insertion.
- Implements cut/snarf/paste using `/dev/snarf` with `tosnarf`, `fromsnarf`, and `cmdmenu`.
- Appends formatted command output with `cmdprint`.

Important interactions:
- Uses Plan 9 `Frame` APIs for text display/editing.
- `cmdprint` writes into global `cmdw`.
- The command menu uses middle mouse button, while right-button handling is partly delegated to the generic app menu.
