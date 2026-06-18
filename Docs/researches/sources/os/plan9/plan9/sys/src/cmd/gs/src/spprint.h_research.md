# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.h

Header for ASCII stream printing helpers.

Key contents:
- Opaque `stream` declaration.
- `stream_putc`, `stream_write`, and `stream_puts`.
- Fixed-arity printing declarations for float, int, long, and string values.
- Comments explain the PDF restriction against exponential float notation and the portability reason for avoiding general varargs.

Notable dependencies:
- Uses `uint` and `floatp` from Ghostscript type context.

Research notes:
- The API returns a pointer to the next format substitution marker so calls can be chained for multi-argument printing.
