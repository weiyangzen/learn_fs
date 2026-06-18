# sources/storage-engines/tikv/components/engine_traits_tests/src/lib.rs

Purpose: Organizes the engine-trait conformance suite and provides common temporary engine constructors.

Important APIs and control flow: The module list includes basic reads/writes, CF names, checkpoints, constructors, delete ranges, iterators, misc, read consistency, scenario writes, snapshots, SSTs, and write batches. `TempDirEnginePair` ensures the engine drops before the tempdir. `default_engine`, `multi_batch_write_engine`, and `engine_cfs` construct `KvTestEngine` instances through `engine_test`; `tempdir` creates isolated directories; `assert_engine_error` validates `Error::Engine`.

State, persistence, and dependencies: Test state is isolated in tempdirs and created through feature-selected concrete engines.

Integration points, risks, and test signals: Provides reusable setup for all shared tests. Risks include feature-selected backend behavior hiding generic contract violations and helper drop-order mistakes causing directory cleanup issues.
