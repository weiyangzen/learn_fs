# sources/storage-engines/tikv/components/in_memory_engine/benches/load_region.rs

Purpose: Criterion benchmark for loading a RocksDB region into the in-memory engine background loader.

Important APIs/types/functions: `bench_load_region`, `bench_with_args`, `prepare_data`, `load_region`, and `MockTsPdClient`.

Control flow: benchmark prepares random MVCC-like data in RocksDB default/write CFs, then repeatedly creates a memory engine and background runner, marks the full data range loading, and calls `run_load_region` with a disk snapshot. Value sizes vary from 32 to 4096 bytes.

State and persistence: temporary RocksDB contains generated input; each iteration creates and drops fresh memory-cache state.

Dependencies/integration: Criterion, Rocks engine, `engine_traits`, `BackgroundRunner`, PD client trait, raftstore split size, random generator, and `txn_types`.

Risks: small sample size/warmup reduce statistical confidence but keep slow benchmark practical; random inputs reduce byte-level determinism.

Test signals: performance signal for background load throughput across value sizes and MVCC amplification.
