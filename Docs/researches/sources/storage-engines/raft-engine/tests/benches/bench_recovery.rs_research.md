# sources/storage-engines/raft-engine/tests/benches/bench_recovery.rs

Purpose: this Criterion benchmark measures `Engine::open` recovery cost over generated raft-engine directories of different sizes and batch/compression patterns.

Important APIs and types: `MessageExtTyped` adapts raft `Entry` indexes. Local `Config` describes benchmark data shape: total data size, region count, batch size, item size, entry size, and compression threshold. `generate` creates a temporary engine directory populated to the target size. `dir_size` sums file sizes in a directory. `bench_recovery` registers the benchmark group.

Control flow: `generate` opens an engine in a tempdir, tracks the last index per region, repeatedly builds `LogBatch`es until directory size reaches the target, fills batches with random entries distributed across regions, writes without sync, syncs once, drops the engine, and returns the tempdir. `bench_recovery` defines default, compressed, small-batch, and 10 GiB configs, prints them, enables a failpoint to skip fadvise effects, generates data for each config, and benchmarks repeated `Engine::open` calls with that directory/config.

State and persistence behavior: benchmark data is persisted in temporary directories for the lifetime of each benchmark input. It intentionally creates realistic append log files and optional compressed batches, then measures recovery from disk by reopening the engine. `TempDir` cleanup removes data afterward.

Dependencies and integration points: depends on Criterion, raft entries, raft-engine `Engine`, `LogBatch`, `ReadableSize`, `MessageExt`, random generation with seeded `StdRng`, `HashMap`, and failpoints. It exercises write/populate/sync before measuring recovery parsing and memtable reconstruction.

Risks and invariants: the 10 GiB config is expensive and can dominate benchmark runtime/disk usage. Writes are unsynced until final sync, which is appropriate for setup but means setup failure modes differ from production sync-per-write workloads. `dir_size` sums immediate directory entries and assumes raft-engine files are direct children. Failpoint cleanup must run after benchmarks to avoid leaking behavior into later tests.

Test signals: Criterion sample size is set in `mod.rs`; this file reports recovery latency across configurations. It is a performance signal, not a correctness assertion, but generation failures or open failures expose recovery incompatibilities.
