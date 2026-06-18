# File Research: sources/teaching/xv6-public/printf.c

User-space `printf` implementation.

Key behavior:
- Writes output one byte at a time to the supplied file descriptor.
- Supports `%d`, `%x`, `%p`, `%s`, `%c`, and `%%`.
- Prints unknown percent sequences literally with `%`.
- Uses uppercase hex digits.

Role:
- Minimal formatted output support for all xv6 user programs.
