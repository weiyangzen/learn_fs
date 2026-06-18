## sources/storage-engines/pebble/tool/make_test_sstables.go

Purpose: build-tagged generator for SSTable fixtures with unusual key ordering and Cockroach key-schema data.

Important APIs/functions: `makeOutOfOrderSST` creates `tool/testdata/000002.sst` with `DisableKeyOrderChecks` and writes keys `a`, `c`, `b` to create an out-of-order SST. `makeCockroachSchemaSST` creates `tool/testdata/000014.sst` using `cockroachkvs.Comparer`, `cockroachkvs.KeySchema`, max table format, small block size, deterministic random KVs, and writes them. `main` runs both generators.

Control flow: each function creates a file through `vfs.Default`, constructs an SSTable writer with appropriate options, writes records, and closes the writer with fatal error handling.

State and persistence: writes two SST fixtures under `tool/testdata`.

Dependencies and integration: uses SSTable writer internals, object-storage file writable, Cockroach key generator, random PCG seed, and VFS. These fixtures are consumed by SSTable/tool datadriven tests outside the main DB command set and may be referenced by corruption/order scenarios.

Risks: disabling key order checks intentionally creates invalid data that should not be used as a normal fixture. Cockroach random KV generation can change if generator semantics change, requiring fixture updates.

Test signals: enables coverage for SSTable validation against out-of-order keys and key-schema-aware table reading/formatting.
