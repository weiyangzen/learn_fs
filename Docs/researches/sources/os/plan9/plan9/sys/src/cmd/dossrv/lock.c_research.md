# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/lock.c

Minimal in-process lock implementation for `dossrv`.

Key behavior:
- `mlock()` sets a one-byte lock key and panics on double lock or uninitialized values.
- `unmlock()` clears the key and panics on unlock errors.
- `canmlock()` is a nonblocking try-lock.

Filesystem relevance:
- Used by FAT allocation and sector-cache structures, but it is only a cooperative sanity lock, not an OS blocking primitive.
