# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/resetlexer.c

Global lexer-state reset helper.

Key behavior:
- Defines global `string_start`, `string_end`, `string_val`, and `pos`.
- `resetlexer()` restores them to initial values.

Research notes:
- This is shared mutable parser state.
