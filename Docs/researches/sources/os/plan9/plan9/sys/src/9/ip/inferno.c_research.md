# File Research: sources/os/plan9/plan9/sys/src/9/ip/inferno.c

Provides small compatibility shims shared between Plan 9 and Inferno variants.

Functions:
- `commonuser` returns `up->user`.
- `commonerror` returns `up->errstr`.
- `bootpread` is a stub returning 0.

Notable use:
- `devip.c` uses `commonuser` for channel attach ownership.
- `bootpread` backs the `bootp` file in this Plan 9 source variant but provides no data here.
