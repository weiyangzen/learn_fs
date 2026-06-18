## sources/sync-backup/syncthing/lib/connections/registry/registry_test.go

Purpose: Verifies registry matching, preferred selection, unregister behavior, duplicate handling, and lookup cost.

Important APIs/types/functions: `TestRegistry`, `TestShortSchemeFirst`, and `BenchmarkGet`. Helper `want` returns preferred predicates over integer test items.

Control flow: Tests register several schemes and values, query compatible schemes, unregister entries, check nil after removal, verify duplicate removal removes only one entry, and ensure shorter scheme wins when preference does not matter.

State and persistence: In-memory test registry only.

Dependencies and integration points: Uses `net.TCPAddr` in benchmark to match real TCP listener registry use.

Risks: Tests model items as ints, so they do not cover non-comparable item misuse or concurrent access.

Test signals: Direct unit tests provide strong signals for intended prefix and tie-breaking behavior.
