# sources/test-tools/syzkaller/pkg/db/db.go

This package implements syzkaller's small append-oriented corpus key-value database. It caches records in memory while mirroring mutations to a compressed binary file, minimizing disk work for syz-manager and syz-hub corpus storage.

The central types are `DB` and `Record`. Public operations include `Open`, `Save`, `Delete`, `DiscardData`, `Flush`, `BumpVersion`, `Create`, `ReadCorpus`, and `Merge`. The on-disk format uses a database header (`dbMagic`, `curVersion`, user version) followed by record entries (`recMagic`, key length/key, sequence, compressed value length/value). `seqDeleted` represents tombstones.

Control flow in `Open` deserializes whatever can be recovered, optionally returns a soft error in repair mode, and compacts to ensure a writable normalized file. `Save` appends pending records unless the same key/value/sequence is already present. `Flush` appends pending bytes and compacts when stale entries dominate. `compact` rewrites a temporary file and atomically renames it. `Merge` accepts both DB files and seed program files, saving valid seeds by hash.

Persistent state is the database file; in-memory state is `Records`, version, uncompacted count, pending write buffer, and `dataDiscarded`. Dependencies include flate compression, binary little-endian encoding, hash generation, target program deserialization, and `osutil` atomic file helpers. Risks include corruption recovery boundaries, decompression bombs, oversized keys, pending-buffer loss before flush, data-discard compaction rereads, and map iteration order during compaction. Tests in `db_test.go` cover basic persistence, modification/tombstones, large data, discard mode, inaccessible/corrupt files, and OOM guards.
