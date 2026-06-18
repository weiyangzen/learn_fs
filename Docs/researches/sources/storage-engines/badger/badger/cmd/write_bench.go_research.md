# sources/storage-engines/badger/badger/cmd/write_bench.go

Purpose: implements `badger benchmark write`, a configurable write workload for Badger performance and stress testing.

Important APIs and flow: flags control key/value sizes, number of keys, sync writes, close compaction, sorted versus random writes, value thresholds, versions, caches, value-log settings, encryption, conflict detection, compression, TTL, periodic `DropAll`, `DropPrefix`, and value-log GC. `writeRandom` writes random keys through `NewManagedWriteBatch` at version 1. `writeSorted` uses `NewStreamWriter` and protobuf KV buffers split into streams. `writeBench` opens Badger managed with chosen options, starts stats/drop/GC goroutines under a `z.Closer`, runs the selected writer, then prints levels.

State and persistence: mutates the DB under `--dir`, can drop all data or prefixes, run value-log GC, and produce large SST/vlog files. Dependencies are Badger managed writes, stream writer, GC/drop APIs, atomics, filesystem walking, and humanize. Risks: `writeRandom` creates one batch for all keys and can grow large, counters/files slices are package-global, periodic destructive operations are easy to enable, and key size/drop-prefix assumptions can panic for small key sizes. Test signals are benchmark output, DB reopen/verification, GC/drop logs, and race/stress runs.
