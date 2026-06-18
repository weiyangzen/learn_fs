## sources/sync-backup/kopia/internal/bigmap/bigmapbench/main.go

Purpose: standalone benchmark/profiling command for comparing `bigmap.Map` against `sync.Map` at very large insertion counts.

Important APIs/types/functions: flags `impl`, `profile-dir`, `profile-cpu`, `profile-memory`, `profile-memory-rate`; `main`; profiling helpers `maybeStartProfiling`, `startCPUProfiling`, and `dumpProfiles`.

Control flow, state, and persistence: generates 300 million SHA-256 keys without allocation, inserts into selected implementation, prints memory and throughput every million inserts, and optionally writes pprof files under the requested profile directory.

Dependencies and integration points: imports `internal/bigmap`, `runtime/pprof`, logging, and clock. It is a developer tool, not library runtime.

Risks and test signals: long-running and resource-intensive; ignores map creation errors in `main`, which is acceptable only for a benchmark utility. No automated tests; profile files are the output signal.
