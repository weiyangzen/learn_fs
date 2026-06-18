# File Research: sources/os/bsd/dragonflybsd/sys/sys/mutex.h

Core DragonFlyBSD mutex structure and non-inline backend declarations.

Key responsibilities:
- Defines `struct mtx_link` for linked/asynchronous mutex acquisition requests with owner, state, callback, and argument.
- Defines cache-aligned `struct mtx` with lock word, flags, exclusive/shared wait links, owner, and identifier.
- Defines initializer macro and lock-state bit layout:
  - `MTX_EXCLUSIVE`
  - shared/exclusive wanted bits
  - link spin bit
  - recursive/shared count mask
- Defines owner sentinel values and link state constants.
- Declares backend functions used by inline wrappers in `mutex2.h`.

Important behavior:
- The mutex supports recursive shared and exclusive locking, downgrade, non-blocking upgrade, blocking and spin forms, and asynchronous link-based acquisition.
- The lock word combines ownership mode, waiter bits, internal spin state, and reference count.
- `MTXF_NOCOLLSTATS` disables collision statistics where not applicable.

Dependencies:
- Kernel/kernel-structures only for structure definitions.
- Includes `types.h`, machine atomics, and CPU functions.
- Backend declarations are kernel-only.

Notable risks:
- Lock word bit layout is tightly coupled to `mutex2.h` fast paths and implementation functions.
- Link state and callback lifetime must be correct for asynchronous/abortable use.
