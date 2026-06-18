# File Research: sources/teaching/xv6-public/ulib.c

Minimal user-space C library helpers.

Implements:
- `strcpy`, `strcmp`, `strlen`, `strchr`.
- `memset` via `stosb`.
- Simple `gets`.
- `stat` wrapper using `open`, `fstat`, and `close`.
- Decimal `atoi`.
- Non-overlap-aware forward `memmove`.

Role:
- Supports xv6 user programs without host libc.
