# File Research: sources/os/plan9/9front/sys/src/cmd/rio/wctl.c

Parser and executor for `rio` `wctl` commands. Supports `new`, `resize`, `move`, `scroll`, `noscroll`, `set`, `top`, `bottom`, `current`, `hide`, `unhide`, and `delete`.

Parses geometry and parameters such as `-r`, min/max coordinates, deltas, `-pid`, `-id`, `-hide`, `-scroll`, `-noscroll`, and `-cd`. Validates rectangles with `goodrect()` and constrains them onscreen.

`writewctl()` dispatches commands either globally or to a target window id, creating windows or sending control messages to existing windows.
