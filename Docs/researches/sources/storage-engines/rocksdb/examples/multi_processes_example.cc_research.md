# sources/storage-engines/rocksdb/examples/multi_processes_example.cc

## Purpose
`multi_processes_example.cc` demonstrates RocksDB primary/secondary operation on Linux. One process creates and writes a primary DB, while another opens the same DB as a secondary, periodically catches up, serves reads, and verifies its view against a read-only primary view.

## Important APIs and control flow
The file is Linux-only; non-Linux builds print "Not implemented." It defines two column families, big-endian-sortable 64-bit key encoders/decoders, random value generation, and an atomic signal flag for secondary shutdown.

`CreateDB()` destroys and recreates the DB, then creates non-default column families. `RunPrimary()` repeatedly opens the DB with all column families, writes `kNumKeysPerFlush` keys per family, flushes each family, advances the key counter, and often closes/reopens to exercise manifest/log durability. `RunSecondary()` installs a SIGINT handler, creates a secondary directory, opens `DB::OpenAsSecondary()`, starts range-scan and point-lookup threads, loops on `TryCatchUpWithPrimary()`, reports observed max keys, and on shutdown verifies key/value equality against `DB::OpenForReadOnly()` on the primary path.

## State, persistence, and integration
The program uses fixed paths under `/tmp` for primary DB, secondary state, and a declared but unused primary-status file. It integrates with Linux directory/signal APIs, RocksDB secondary instances, flushing, iterators, read options with checksum verification and total-order seek, and column family descriptors.

## Risks and test signals
The secondary verification opens only default iterators despite defining multiple column families, so it does not fully verify every CF. The key decoder treats `char` values as signed in the non-little-endian branch, which is a portability risk, though the example is Linux-focused. Threads share one secondary `DB` for reads, which RocksDB supports, but iterator status is not checked after scans. Fixed paths can collide. Test signals are successful two-terminal execution, secondary catch-up progress, concurrent range/point reads without errors, SIGINT shutdown, and final verification success.
