<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/atomic_utils.h -->
# sources/user-network-fs/nfs-ganesha/src/include/atomic_utils.h

## Purpose
`atomic_utils.h` builds higher-level refcount helpers on top of `abstract_atomic.h`. Its helpers decrement a refcounter and acquire a mutex only for the final-reference path.

## Important APIs, types, and functions
- `PTHREAD_MUTEX_dec_int64_t_and_lock()`
- `PTHREAD_MUTEX_dec_uint64_t_and_lock()`
- `PTHREAD_MUTEX_dec_int32_t_and_lock()`
- `PTHREAD_MUTEX_dec_uint32_t_and_lock()`

Each helper accepts a pointer to a refcounter and a mutex. It returns true when the counter was decremented to zero and the mutex remains locked for caller cleanup.

## Control flow
The helpers first try `atomic_add_unless_*(&refcount, -1, 1)`. If the count was greater than one, the decrement succeeds and no lock is taken. If the count might be one, the helper locks the mutex, decrements under the mutex, and returns true if the result is zero. If another reference appeared, it unlocks and returns false.

## State and persistence
The header mutates caller-owned refcount and mutex state. It has no independent state or persistence.

## Dependencies and integration points
It depends on `common_utils.h` for pthread lock wrappers and `abstract_atomic.h` for add-unless and arithmetic helpers. It is intended for object lifetime code where cleanup must be serialized by a mutex only at the zero-ref transition.

## Risks
- Unsigned variants pass `-1` to unsigned add helpers, relying on wraparound to decrement. This is idiomatic here but easy to misuse.
- Callers must understand that true means the mutex is locked and must be unlocked after destruction/cleanup.
- The pattern assumes references cannot be safely resurrected after the zero path starts without holding the same mutex.
- Passing a zero refcount underflows; caller invariants must prevent double put.

## Test signals
- Unit tests should cover decrement from counts greater than one, exactly one, and concurrent final puts.
- Tests should verify true return leaves the mutex locked and false return leaves it unlocked.
- Sanitizer or assertion tests should catch double-decrement or zero-ref misuse in caller code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/atomic_utils.h -->
