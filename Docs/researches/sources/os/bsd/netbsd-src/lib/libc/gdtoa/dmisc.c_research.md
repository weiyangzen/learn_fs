# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/dmisc.c

Provides miscellaneous dtoa allocation and bigint division helpers. `rv_alloc` allocates a `Bigint` block large enough for a returned string and stores the allocation size class just before the returned character pointer; in non-threaded builds it also records `dtoa_result`. `nrv_alloc` allocates and copies a null-terminated string and optionally returns the end pointer. `freedtoa` converts a returned string pointer back to its owning `Bigint` block and frees it.

`quorem` divides a `Bigint` numerator by another `Bigint` denominator known to produce a single decimal digit quotient. It estimates `q`, subtracts `q*S` from `b` with carry/borrow handling for 32-bit, packed-16, or `ULLong` arithmetic, normalizes word counts, then subtracts once more if the remainder is still at least `S`.

Dependencies: `gdtoaimp.h` for `Bigint`, `Balloc`, `Bfree`, `cmp`, arithmetic typedefs, and packing macros.

Risks/invariants: returned dtoa strings must be freed with `freedtoa`, especially in threaded builds. `quorem` assumes `b->wds <= S->wds` plus quotient digit bounds enforced by callers.
