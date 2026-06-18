# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/atomic.h

This header implements a small Linux `atomic_t` compatibility layer on top of Windows interlocked primitives.

Key definitions:
- `atomic_t` wraps a volatile `LONG counter`.
- `ATOMIC_INIT`, `atomic_read`, and `atomic_set`.
- Arithmetic helpers: `atomic_add`, `atomic_sub`, `atomic_inc`, `atomic_dec`.
- Test helpers: `atomic_sub_and_test`, `atomic_dec_and_test`, `atomic_inc_and_test`, `atomic_add_negative`.

Implementation notes:
- Uses `InterlockedExchange`, `InterlockedExchangeAdd`, `InterlockedIncrement`, `InterlockedDecrement`, and `InterlockedCompareExchange`.
- `atomic_sub_and_test` loops with compare-exchange to return whether the post-subtract result is zero.

Notable risk:
- `atomic_add_negative` returns the arithmetic post-add value, not a strict boolean negative test, despite the Linux-style function name.
