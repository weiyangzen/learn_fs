# sources/storage-engines/foundationdb/layers/containers/set.py

Purpose: This Python 2 example implements a sorted set abstraction on FoundationDB using tuple-encoded keys. It mirrors many Python set operations while preserving ordered iteration.

Important APIs and types: `FdbSet` exposes `length`, `iterate`, `contains`, `issubset`, `issuperset`, `union`, `intersection`, `difference`, `symmetric_difference`, in-place update variants, `add`, `remove`, `discard`, `pop`, `clear`, and ordered seek helpers. `nextStopToNone` adapts generator exhaustion.

Control flow: Each set member is stored as key `(path, member)` with an empty value. Merge-style operations iterate two sorted key streams or use `first_greater_or_equal` to skip ahead. In-place operations delete ranges or individual keys while scanning intersections.

State and persistence behavior: The persisted set is the key range starting with the tuple prefix for `_path`. There is no metadata key for size, so `length` scans all members. `remove` raises `KeyError` when the key is absent, while `discard` is idempotent.

Dependencies and integration points: It uses `fdb.api_version(16)` and tuple keys. The file includes a destructive `test(db)` that clears the database and prints behavior, and it opens the default database at import-time.

Risks: The module-level `db = fdb.open(); test(db)` makes importing the file destructive. `_keyInRange` uses tuple-prefix string arithmetic and can be fragile for non-string paths. Tests should isolate a subspace, remove import-time side effects, and validate every set algebra operation, ordered seeking, empty pop, and range deletion behavior.
