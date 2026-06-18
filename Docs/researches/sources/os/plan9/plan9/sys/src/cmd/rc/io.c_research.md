# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/io.c

Buffered I/O and custom formatting for rc.

Capabilities:
- `pfmt()` implements rc-specific formatting: chars, decimals, octal, pointers, quoted words, error strings, command trees, and word lists.
- `pchr()`, `fullbuf()`, `flush()` handle output buffering to fd-backed or string-backed `io`.
- `rchr()`, `emptybuf()`, `rutf()` handle buffered byte/rune input.
- `pquo()`, `pwrd()`, `pval()` print shell-safe quoted words/lists.
- `pdec()`, `poct()`, `pptr()`, `pstr()` are lightweight format primitives.
- `openfd()`, `openstr()`, `opencore()`, `rewind()`, `closeio()` construct and manage `io` objects.

Risk/notes:
- String-backed `io` grows in `Stralloc` chunks.
- `flush()` can trigger traps if writes fail while traps are pending.
- `rutf()` may push back unconsumed bytes for malformed/partial UTF.
