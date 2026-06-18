# File Research: sources/os/bsd/freebsd-src/sys/sys/_atomic64e.h

Kernel-only declarations for emulated 64-bit atomic operations on platforms that lack native support.

Defines:
- `HAS_EMULATED_ATOMIC64`.
- Prototypes for add, cmpset, fcmpset, clear, fetchadd, load, readandclear, set, subtract, store, and swap on `u_int64_t`.
- Acquire/release variants are aliases to the base emulated functions.

Constraints:
- Must be included through `<machine/atomic.h>`; direct inclusion triggers `#error`.
- Exposed only under `_KERNEL`.

Research relevance:
- Architecture abstraction layer for FreeBSD atomic APIs, preserving a common kernel atomic interface across weaker platforms.
