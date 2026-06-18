# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/sprite.h

Compatibility type header from Sprite/BSD lineage.

Key elements:
- Defines integer `Boolean`, `TRUE`, `FALSE`, `ReturnStatus`, `SUCCESS`, `FAILURE`, `NIL`, `USER_NIL`, `NULL`, `Address`, and `ClientData`.
- `ClientData` is `void *`.

Dependencies:
- Used by `hash.h`/`hash.c`.

Research notes:
- The header exists to support imported generic hash code rather than FreeBSD-wide conventions.
