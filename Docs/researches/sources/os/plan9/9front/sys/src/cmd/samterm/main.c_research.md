# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/main.c

`main.c` is samterm's main UI loop and local editing front end.

`threadmain` initializes display, icons, I/O, scratch buffer, the command window, sends version/start messages, then loops over host, plumb, keyboard, mouse, and resize events. It handles current layer selection, scrolling, selection, chording, menus, and terminal protocol calls.

`current`, `closeup`, `duplicate`, `getr`, and `resize` manage active layers, closing/duplicating text windows, interactive rectangle selection, and resize-time host checks.

Editing operations include `snarf`, `cut`, `paste`, `type`, `flushtyping`, and movement/delete helpers. Local typing is applied optimistically to the terminal rasp and frame via `hgrow`/`hdatarune`, batched as `Ttype`, and flushed on newline or size thresholds.

Keyboard handling supports arrow/page/home/end scrolling, line start/end, command-window jump, work-window cycling, escape selection of typed text, backspace/delete/ctrl-u/ctrl-w deletion, autoindent, and spaces-for-tabs indentation.

`center` requests origin changes locally or from the host. `gettext` loads frame text from a `Rasp`, `scrtotal` reports total runes, and `alloc` is a zeroing panic-on-failure allocator.
