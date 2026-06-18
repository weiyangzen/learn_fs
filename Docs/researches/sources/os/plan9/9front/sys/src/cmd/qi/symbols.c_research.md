# File Research: sources/os/plan9/9front/sys/src/cmd/qi/symbols.c

Symbol, source-location, and stack-trace helpers for `qi`.

Key responsibilities:
- `printsource` maps a PC to `file:line`.
- `printlocals` prints automatic variables for a function frame.
- `printparams` prints parameter values using frame pointer offsets.
- `stktrace` walks stack frames using `.frame` symbols, link register/saved PC conventions, and prints call chains; `C` modifier includes locals.

Dependencies and coupling:
- Uses Plan 9 `mach` symbol APIs and memory accessors.
- Used by command handling and call-tree tracing.

Notable behavior:
- Stops at `_main` and truncates after 40 frames.
