# File Research: sources/teaching/os161/kern/include/limits.h

Kernel-facing wrapper for exported system limits.

Key behavior:
- Includes `<kern/limits.h>`.
- Maps private `__NAME_MAX`, `__PATH_MAX`, etc. to public names like `NAME_MAX`, `PATH_MAX`, `ARG_MAX`, `OPEN_MAX`, and `IOV_MAX`.

Relevance:
- Kernel code uses this wrapper for conventional limit names while preserving namespace hygiene in shared ABI headers.
