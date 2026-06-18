# sources/security-integrity/cryfs/crates/utils/src/containers.rs

Purpose: collection extension traits for fallible insertion into `HashMap` and `HashSet`.

Important APIs/types/functions: `HashMapExt::try_insert` returns `&mut V` or `OccupiedError` containing the existing occupied entry and rejected value. `HashSetExt::try_insert` returns an error if the item already exists.

Control flow: HashMap implementation uses entry API. HashSet implementation checks `contains`, then inserts and asserts success.

State/persistence: mutates caller-owned collections only.

Dependencies/integration: `AsyncDropHashMap` depends on the HashMap extension to avoid replacing existing async-drop guards.

Risks: HashSet check-then-insert hashes twice. `OccupiedError` exposes an occupied entry, which can be useful but extends borrow complexity.

Test signals: unit tests cover new insertion, mutable return, duplicate failure, error contents/display, and hashset duplicate handling.
