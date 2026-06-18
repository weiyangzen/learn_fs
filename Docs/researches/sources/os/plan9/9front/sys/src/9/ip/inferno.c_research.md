# File Research: sources/os/plan9/9front/sys/src/9/ip/inferno.c

Small compatibility shim for code shared between Inferno and Plan 9 variants of the IP stack.

Key responsibilities:
- `commonuser()` returns the current process user via `up->user`.
- `commonerror()` returns the current process error string via `up->errstr`.
- `bootpread()` is a stub returning 0.

Dependencies and integration:
- Included by Plan 9 networking code that expects common user/error abstraction.
- `bootpread()` is called by `devip.c` when reading the top-level `bootp` file.

Research notes:
- No protocol logic is implemented here.
- The file exists to smooth portability/common-source differences.
