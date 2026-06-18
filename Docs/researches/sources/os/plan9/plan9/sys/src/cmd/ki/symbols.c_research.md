# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/symbols.c

This file provides source and symbol-aware reporting for `ki`.

`printsource()` maps a text address to `file:line` using `fileline()`. `printlocals()` prints automatic variables for a function frame by reading from emulated memory. `printparams()` prints function parameters from the frame.

`stktrace()` walks frames using symbol data, `.frame` locals, saved PC/SP conventions, and fallback handling for leaf/local symbols. It prints function calls, parameter values, source locations, callers, and optionally locals for `$C`.

The stack trace stops at `_main`, fails out if frame metadata is missing, and truncates after 40 frames.
