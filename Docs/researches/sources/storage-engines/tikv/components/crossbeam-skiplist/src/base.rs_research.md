# sources/storage-engines/tikv/components/crossbeam-skiplist/src/base.rs

Purpose: This is the lock-free skip-list core used by the public map and set wrappers. It implements ordered concurrent insertion, removal, search, range iteration, bidirectional traversal, and owned/reference-counted entry handles on top of `crossbeam_epoch`.

Important APIs and types: Public surface includes `SkipList<K,V>`, guarded `Entry<'a,'g,K,V>`, reference-counted `RefEntry<'a,K,V>`, `Iter`, `RefIter`, `Range`, `RefRange`, `IntoIter`, and `OwnedIter`. Internal types include dynamically sized `Node`, `Tower`, `Head`, `Position`, `HotData`, and `OwnedEntry`. Key methods are `new`, `len`, `front`, `back`, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `get_or_insert_with`, `insert`, `compare_insert`, `remove`, `pop_front`, `pop_back`, `clear`, and traversal helpers.

Control flow: Searches start at the highest non-empty head level, move right while bounds allow, and drop levels until level 0. Encountered marked pointers trigger `help_unlink`, which tries to splice deleted nodes out and decrement level references. Insertion searches a position, optionally marks an existing equal key for replacement, allocates a node with a random height, CAS-installs level 0, then opportunistically builds higher tower levels. Removal marks the node tower, decrements approximate length, and unlinks each level or falls back to a search that helps unlink.

State and persistence behavior: All state is volatile memory. `HotData` tracks a relaxed pseudo-random seed, approximate length, and max tower height. Node lifetime is controlled by a packed height/reference counter and deferred epoch reclamation; `RefEntry` and iterator cursor references must be released with an epoch guard, while public wrappers hide that detail.

Dependencies and integration points: It depends on `alloc`, `core`, `crossbeam_epoch::{Atomic, Collector, Guard, Shared}`, and `crossbeam_utils::CachePadded`. `map.rs` wraps it with default collector pinning; tests exercise both direct guarded APIs and public wrappers.

Risks: The implementation is unsafe-heavy: dynamic allocation layout, pointer tagging, relaxed/SeqCst ordering choices, guard-collector matching, and manual reference release are all correctness-critical. `RefEntry` leaks if `release` is never called, and delayed global epoch collection explains the `'static` bounds on mutating APIs. Length is approximate during concurrent mutation and can clamp underflow to zero.

Test signals: `tests/base.rs` covers creation, replacement, removal, bounds, ranges, iteration under deletion, panic safety in `get_or_insert_with`, concurrent closure races, owned iteration, clear, and destructor counts after epoch flushing.
