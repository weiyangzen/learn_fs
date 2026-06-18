# File Research: sources/os/plan9/9front/sys/src/cmd/rc/io.c

Buffered I/O and minimal formatter for `rc`. Supports file-backed buffers and expandable in-memory string buffers.

Provides `pfmt()`/`vpfmt()` with shell-specific verbs for commands, words, values, quoted strings, pointers, decimal/octal values, and opcode names. Provides `rchr()` and `rstr()` for lexer and command-substitution reads.

`flushio()` either writes pending bytes to an fd or grows memory buffers. Write failures can trigger pending trap delivery.
