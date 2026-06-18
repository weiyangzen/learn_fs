<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_atomic.h -->
# sources/user-network-fs/nfs-ganesha/src/include/abstract_atomic.h

## Purpose
`abstract_atomic.h` is Ganesha's inline atomic-operation shim over GCC `__atomic` builtins. It provides named helpers for arithmetic, bit operations, fetch/store, compare-add-unless, and a small number of relaxed counters across common integer, pointer, time, and size types.

## Important APIs, types, and functions
- Pre-operation arithmetic helpers return the value after mutation, for signed and unsigned 8/16/32/64-bit integers and `size_t`: `atomic_add_*`, `atomic_inc_*`, `atomic_sub_*`, and `atomic_dec_*`.
- Post-operation helpers return the value before mutation: `atomic_postadd_*`, `atomic_postinc_*`, `atomic_postsub_*`, and `atomic_postdec_*`.
- Bit helpers for unsigned 8/16/32/64-bit integers include pre and post clear/set operations.
- Fetch/store helpers cover `size_t`, `ptrdiff_t`, `time_t`, `uintptr_t`, `void *`, and integer widths.
- `atomic_add_unless_*()` exists for 32/64-bit signed and unsigned counters and uses a compare-exchange loop.
- `atomic_inc_unless_0_int32_t()` increments a nonzero int32 refcount and returns the new value or zero.
- `atomic_relaxed_add_int32_t()` and `atomic_relaxed_inc_int32_t()` use relaxed ordering for counters that do not need synchronization.

## Control flow
Most helpers are single inline wrappers around `__atomic_*` with `__ATOMIC_SEQ_CST`. The add-unless functions first load the current value, return false if it equals the sentinel, otherwise retry compare-exchange until the mutation succeeds. Relaxed helpers explicitly choose `__ATOMIC_RELAXED`.

## State and persistence
The header has no state. It mutates caller-owned memory atomically and establishes memory-ordering semantics for concurrent runtime state such as refcounts, cache hints, counters, and flags.

## Dependencies and integration points
It depends on `<stddef.h>`, `<stdint.h>`, `<time.h>`, `<stdbool.h>`, and compiler support for GCC/Clang `__atomic` builtins. It is used broadly by cache code, client manager refcounts, state counters, and synchronization utilities such as `atomic_utils.h`.

## Risks
- The file assumes compiler support for `__atomic`; unsupported compilers have no fallback here.
- Nearly all operations are sequentially consistent, which is simple but may be more expensive on hot counters.
- Unsigned add-unless with `-1` arguments relies on unsigned wraparound in callers such as refcount decrement helpers.
- Atomic pointer helpers do not solve object lifetime; callers still need locks or refcounts to keep pointed-to memory valid.
- Type-specific duplication makes it easy for one helper to drift in signature or semantics from the others.

## Test signals
- Compile tests should cover every helper on all supported architectures and detect missing builtins.
- Unit tests should validate pre/post return values, bit set/clear results, fetch/store behavior, add-unless sentinel behavior, and relaxed counter arithmetic.
- Threaded stress tests should exercise refcount-like add-unless loops under contention.
- Static analysis should flag misuse of pointer atomics without lifetime protection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_atomic.h -->
