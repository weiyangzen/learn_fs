# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/error.c

Read status: complete, 144 lines.

This file maps `sam` error and warning enums to user-facing messages. `error`, `error_s`, `error_r`, and `error_c` format fatal command errors and pass them to `hiccough`. Warning functions print terminal warnings with string or `String` arguments.

`termwrite` writes messages either into the downloaded command file state or directly to fd 2, depending on whether the graphical terminal is connected.

Filesystem relevance: indirect; includes I/O error messages and routes diagnostics through terminal/file buffers.
