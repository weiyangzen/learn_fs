# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/samterm.h

Purpose: Central header for samterm, declaring editor-terminal data structures, process-wide globals, and cross-file function prototypes.

Key definitions:
- `Section`: one rasp span, with rune count, optional cached text, and next pointer.
- `Rasp`: sparse per-text document cache.
- `Text`: a samterm file/window model with rasp, tag, lock state, and `Flayer` screen layers.
- `Readbuf`: fixed-size host/plumb communication buffer.
- `Resource`: host, keyboard, mouse, plumb, and resize event resource IDs.

Exports and globals: Declares text/name/tag tables, cursor state, current layer pointers, command text, host/plumb channels, input controls, configuration flags, and host protocol output functions.

Integration: Includes `mesg.h` and ties together UI, host communication, text editing, scrolling, menu handling, rasp cache management, and display flushing.

Risks and invariants:
- Many globals are shared mutable state, so call ordering is part of the contract.
- `MAXFILES`, `READBUFSIZE`, and `NL` bound major runtime resources.
- `Untagged` uses `65535` as a sentinel tag value.
