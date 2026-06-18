# sources/storage-engines/tikv/components/concurrency_manager/src/lock_table.rs

Purpose: implements the ordered in-memory table mapping transaction keys to weak references of per-key `KeyHandle`s.

Important APIs and types: `LockTable(pub Arc<SkipMap<Key, Weak<KeyHandle>>>)`, `lock_key`, `check_key`, `check_range`, `get`, `find_first`, `for_each`, `for_each_kv`, and `remove`.

Control flow: `lock_key` creates a candidate handle and pre-locks it, inserts its weak pointer with `get_or_insert`, and either returns the candidate guard if inserted or upgrades and locks the existing handle. If an existing weak pointer cannot be upgraded, it loops until a live handle is found or inserted. Range and full-table scans upgrade weak values before inspecting lock payloads.

State and persistence: stores weak pointers in a concurrent skiplist. Actual lock data lives in `KeyHandle`; stale skiplist entries are removed by `KeyHandle::drop`.

Dependencies and integration: used by `ConcurrencyManager` for lock acquisition and read conflict checks. Depends on the local forked `crossbeam_skiplist::SkipMap`, transaction `Key` ordering, and `KeyHandle`.

Risks: weak-pointer lifecycle is subtle; stale entries can temporarily exist and force retry/skip behavior. Range scans are ordered but not snapshot-isolated across concurrent mutation. `remove` blindly removes by key and relies on correct handle lifetime.

Test signals: tests cover same-key serialization, point/range checks, full iteration, and reacquiring keys after handles drop so that table entries point to live handles.
