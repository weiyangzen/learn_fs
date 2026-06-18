# File Research: sources/os/bsd/freebsd-src/sys/sys/_mutex.h

Mutex structure definitions.

Key elements:
- Defines `struct mtx` with common `lock_object` and volatile `mtx_lock`.
- Defines cache-line-aligned `struct mtx_padalign` with mirrored fields.

Dependencies:
- Includes `sys/_types.h`, `sys/_lock.h`, and `machine/param.h`.

Research notes:
- The member name `mtx_lock` is reserved for mutex implementations.
- Pad-aligned form is intended to be API-compatible while avoiding false sharing.
