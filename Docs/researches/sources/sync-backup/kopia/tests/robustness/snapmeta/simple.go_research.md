<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/simple.go

This file implements an in-memory metadata store. `Simple` stores key/value byte slices and an `Index`. It satisfies the robustness store behavior for tests and for the legacy Kopia persister before flushing whole metadata.

The important methods are constructor `NewSimple`, `Store`, `Load`, `Delete`, and index helper forwarding methods. `Load` returns `robustness.ErrKeyNotFound` for absent keys; `Store` copies or assigns values into the map; `Delete` removes keys.

State is JSON-serializable in-memory metadata. Risks include lack of synchronization for concurrent access, byte-slice aliasing depending on implementation details, and index consistency being caller-managed rather than automatic. Direct tests validate basic store/index behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple.go -->
