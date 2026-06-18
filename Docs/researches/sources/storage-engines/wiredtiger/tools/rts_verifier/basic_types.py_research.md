# sources/storage-engines/wiredtiger/tools/rts_verifier/basic_types.py

Purpose: defines the small domain model used by the rollback-to-stable verbose-log verifier.

Important APIs and control flow: enums `PrepareState`, `UpdateType`, and `PageType` mirror WiredTiger RTS values seen in verbose messages. `Timestamp` stores `(start, stop)` pairs and implements equality and ordering by tuple comparison. `Tree` stores a filename and mutable `logged` flag, with equality/hash based on file. `Page` stores an address and mutable `modified` flag, with equality/hash based on address.

State and persistence behavior: instances are in-memory only. `Tree.logged` and `Page.modified` are populated by `Checker` as log lines are processed.

Dependencies and integration points: imported by `operation.py` for parsing enum names and by `checker.py` for visited tree/page tracking.

Risks: enum values must stay synchronized with logged symbol names and parser expectations. `Tree.__eq__` and `Page.__eq__` assume `other` has the same attributes. Timestamp ordering is lexicographic and does not encode any WiredTiger-specific timestamp validity rules.

Test signals: no direct tests in this subset. Parser failures in `Operation` are the main signal that enum names drifted.
