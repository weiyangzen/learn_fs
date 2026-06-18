# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/refcount.h

This header declares ZFS debug-aware reference counters. In debug builds it tracks owners and reference numbers; in non-debug builds it compiles down to atomic count operations.

Core definitions:
- `FTAG` uses the current function name as a holder tag for function-scoped holds.
- `zfs_refcount_t` in debug builds stores count, mutex, AVL tree of active references, removed-reference list/count, and tracking mode.
- `reference_t` records holder tag, removed marker, reference number, and search/link state.
- Non-debug `zfs_refcount_t` is just a `uint64_t rc_count` with macro implementations.

Public API surface:
- Create/destroy tracked or untracked counters, including destroy with expected count.
- Count/zero queries and add/remove single references.
- `add_few`/`remove_few` adjust many independently removable references.
- `add_many`/`remove_many` add one tracked reference with a larger reference number that must be removed as a unit.
- Transfer counts or transfer ownership tags, and query whether a holder has or lacks a reference.
- Global `zfs_refcount_init()` / `zfs_refcount_fini()` exist only for debug tracking support.

Risk-sensitive invariants:
- Debug `add_many()` and `remove_many()` semantics are not equivalent to repeated single-reference operations.
- Holder tags are correctness aids in debug builds and become largely advisory in non-debug builds.
- Non-debug held checks only prove the count is nonzero, not ownership by a specific holder.
