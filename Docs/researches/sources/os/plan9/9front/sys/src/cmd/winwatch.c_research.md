# File Research: sources/os/plan9/9front/sys/src/cmd/winwatch.c

Graphical rio window watcher/switcher. It displays other windows as labeled rows, tracks visibility/current state, and lets the user rename or hide/unhide windows.

Key behavior:
- Periodically reads `/dev/wsys`, excluding its own window id and optional regexp-matched labels.
- For each window, reads label and `wctl`, extracts current/visible state, and stores a compact `Win` record.
- Computes a row/column grid based on font height and screen size, then draws colored rectangles with labels and borders.
- Middle-click on an entry prompts for a new label and writes it to `/dev/wsys/<id>/label`.
- Right-click toggles hide/unhide, raises the target to top, and marks it current through `/dev/wsys/<id>/wctl`.
- Keyboard `q` or delete exits; timer refreshes every 2.5 seconds.

Notable dependencies:
- Plan 9 draw/event/cursor/regexp/keyboard APIs and rio `/dev/wsys` control files.

Research notes:
- State colors distinguish not-visible/current/visible combinations through `statecol[state]`.
- Directory entries are processed in the order returned by `/dev/wsys`.
