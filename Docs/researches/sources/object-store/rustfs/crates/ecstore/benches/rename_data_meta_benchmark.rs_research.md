# sources/object-store/rustfs/crates/ecstore/benches/rename_data_meta_benchmark.rs

Purpose: Criterion benchmark for file metadata read-modify-write behavior during data/meta rename or version replacement paths.

Important APIs and functions: `make_file_info` creates a `rustfs_filemeta::FileInfo` with version ID, data directory, size, mod time, metadata, and erasure layout. `build_meta_with_versions` seeds a `FileMeta` with 1, 8, 32, or 64 versions. The benchmark exercises `FileMeta::load`, `find_unshared_data_dir_for_version`, `data.remove_two`, `add_version`, and `marshal_msg`.

Control flow: for each version count, it serializes seeded metadata, picks the first version ID for replacement, and compares three paths: full read-modify-write, prepared add-version plus marshal, and remove-only after load.

State and persistence: no disk state; serialized metadata buffers model on-disk xlmeta-like state in memory.

Dependencies and integration points: directly targets `rustfs-filemeta`, UUID version/data-dir identifiers, erasure metadata layout, and time-based version ordering.

Risks: deterministic structure may not capture all production metadata complexity. Benchmark includes UUID generation for replacement versions in some paths, which may affect timing.

Test signals: performance insight for versioned metadata mutation hot paths, especially as version count grows.
