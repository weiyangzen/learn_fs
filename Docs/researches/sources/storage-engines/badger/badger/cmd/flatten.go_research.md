# sources/storage-engines/badger/badger/cmd/flatten.go

Purpose: implements `badger flatten`, which forces LSM compactions to consolidate tables into one level.

Important flow: flags configure compactor worker count, number of versions, encryption key file, and compression type. `flatten` normalizes nonpositive version count to `math.MaxInt32`, reads an encryption key with `getKey`, validates compression type `0..2`, opens Badger with compactions disabled (`WithNumCompactors(0)`), explicit cache sizes, compression and encryption options, then calls `db.Flatten(fo.numWorkers)`.

State and persistence: mutates the DB's LSM table layout and may rewrite SSTables. Dependencies include Badger `Flatten`, options compression enum, and key-file reading from `rotate.go`. Risks: it opens the DB read-write and is best run without concurrent writers; high worker counts increase compaction pressure; invalid compression is rejected but empty key path means plaintext mode. Test signals should include post-restore flatten workflows, encrypted DB opening, compression combinations, and no-concurrent-write operational tests.
