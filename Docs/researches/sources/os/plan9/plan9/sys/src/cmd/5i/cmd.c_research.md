# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/cmd.c

## Scope

Interactive debugger command parser and formatter for `5i`.

## Behavior

- Parses expressions from symbols, `#hex`, decimal/octal forms, and one binary operator.
- Handles debugger commands: break/delete/run/continue/step, register/stat dumps, trace flags, memory examine, expression evaluate, and register assignment.
- `pfmt()` prints guest memory or values in numeric, character, string, address, disassembly, source, and global-symbol formats.
- Installs interrupt handler that stops emulation and resumes command processing.

## Dependencies

Uses `bio` I/O, Mach symbol/disassembly APIs, emulator memory APIs, and command helpers from other `5i` files.

## Risks And Invariants

- String memory formats copy into fixed 1024-byte buffers until a guest NUL byte; no explicit bound check in that loop.
- Expression grammar is intentionally minimal.
- Repeating an empty line reuses `lastcmd`; `buf` and `lastcmd` are fixed 128-byte arrays.
