# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/main.c

Contains the `samterm` UI main loop and interactive editing behavior.

Key responsibilities:
- `threadmain` initializes screen, icons, I/O, command rasp/flayer, sends protocol `Tversion`, starts the command file, and runs the event loop.
- Handles host messages, plumb inserts, keyboard typing, mouse selection, scrolling, menus, window creation/duplication/resize/close.
- Maintains active layer globals `which` and `work`, typing coalescing (`typestart`, `typeend`, `typeesc`), snarf length, and host lock state.

Key functions:
- `resize`, `current`, `closeup`, `findl`, `duplicate`, `getr`.
- `snarf`, `cut`, `paste`, `scrorigin`.
- `ctlw`, `ctlu`, `center`, `onethird`, `flushtyping`, `nontypingkey`, and `outcmd`.
- `gettext`, `scrtotal`, and `alloc`.

Behavior notes:
- Typing is buffered locally and flushed as `Ttype`/selection updates to reduce protocol chatter.
- Command text gets special handling for send, newline execution, and plumb injection.
- Non-typing keys implement navigation, deletion, line start/end, paging, and control-editing behavior.
