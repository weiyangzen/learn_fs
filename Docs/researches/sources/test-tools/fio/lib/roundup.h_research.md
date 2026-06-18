# sources/test-tools/fio/lib/roundup.h

Purpose: rounds an unsigned depth up to a power-of-two-style size used for log buffers.

Important APIs/functions: `roundup_pow2(unsigned depth)` returns `1UL << __fls(depth - 1)`.

Control flow/state: pure inline computation using `__fls` from `lib/fls.h`. For powers of two it returns the same value; for non-powers it returns the next power of two.

Dependencies/integration: included by iolog setup to size pending sample buffers when iodepth exceeds default entries.

Risks/test signals: `depth == 0` underflows before `__fls`; callers must avoid zero. Tests should cover powers, non-powers, and documented caller preconditions.
