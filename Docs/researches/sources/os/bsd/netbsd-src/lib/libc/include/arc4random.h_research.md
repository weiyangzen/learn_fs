# File Research: sources/os/bsd/netbsd-src/lib/libc/include/arc4random.h

Private libc header for `arc4random` global and per-thread state.

Defines:
- `struct crypto_prng` with 32-byte state.
- `struct arc4random_prng` with PRNG state and epoch.
- `struct arc4random_global_state` with mutex, thread key, global PRNG, once control, and flags for initialization, fork safety, and per-thread mode.
- `arc4random_global` macro remapped to private symbol `__arc4random_global`.

Depends on `reentrant.h` for mutex/thread/once types.
