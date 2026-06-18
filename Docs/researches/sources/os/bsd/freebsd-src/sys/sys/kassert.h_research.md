# File Research: sources/os/bsd/freebsd-src/sys/sys/kassert.h

Defines kernel and standalone assertion infrastructure. Kernel builds expose `panicstr`, `KERNEL_PANICKED()`, panic/vpanic declarations, and optional `kassert_panic` behavior depending on WITNESS/INVARIANT support.

With `INVARIANTS`, it enables `KASSERT`, vnode/mount assertions (`VNASSERT`, `MPASSERT`, `VNPASS`, `MPPASS`), poison-pointer debugging, and unreachable-segment panics. Without invariants, most checks compile away.

Also provides `CTASSERT`, `MPASS` variants, atomic pointer load alignment assertion, and `CRITICAL_ASSERT` for checking thread critical-section nesting.
