# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.h

Declares the public random-state API used by Unbound utility code.

Key API:
- Opaque `struct ub_randstate`.
- `ub_initstate(struct ub_randstate* from)` allocates and initializes a generator state.
- `ub_random(struct ub_randstate* state)` returns a 31-bit random value.
- `ub_random_max(struct ub_randstate* state, long int x)` returns an unbiased value in `[0, x - 1]`.
- `ub_randfree(struct ub_randstate* state)` frees the state.

Contract notes:
- `x` for `ub_random_max` must be positive and less than `2^31`.
- The header describes thread-safe, repeatable per-state random use, similar to `arc4random()` but with explicit initialization.
- The `from` parameter is documented as a possible seed source, though the OpenBSD/Unbound implementation in this group ignores it for the active backends.
