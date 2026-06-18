# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/input.c

This file implements eqn’s layered input system: files, strings, macros, pushed-back characters, includes, macro arguments, and error context printing.

Key responsibilities:
- Maintains an input source stack with `pushsrc` and `popsrc`.
- Supports macro argument collection in `dodef` and `getarg`.
- Reads characters from files, strings, macros, free strings, and pushback in `input`.
- Handles `$n` macro argument expansion.
- Implements `unput` and `pbstr`.
- Reports errors with file/line context and recent input around the error in `eprint`.

Important implementation notes:
- Includes close files and restore previous `.lf` line directives when popped.
- `eprint` injects `\n.EN\n` as a recovery/safety pushback after errors.
- Macro argument storage uses fixed-size frames and buffers, reflecting old eqn constraints.
