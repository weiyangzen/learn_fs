# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/subr.c

Small rc utility and error helpers.

Functions:
- `emalloc()` wraps platform `Malloc()` and panics on failure.
- `efree()` wraps `free()` and reports attempts to free nil.
- `yyerror()` reports parser errors with file/line/token context, resets lexer continuation state, skips to newline/EOF, increments `nerror`, and sets status.
- `inttoascii()` converts signed integers through recursive helper `iacvt()`.
- `panic()` prints an internal error and aborts.

Risk/notes:
- `iacvt()` does not handle the most negative integer correctly, as commented.
- `yyerror()` consumes input until line end to recover parser state.
