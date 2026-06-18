# sources/test-tools/crashmonkey/code/permuter/Permuter.h

Purpose: declares the abstract permuter interface and shared epoch/sector data structures used to generate crash states from logged writes.

Important APIs/types: `epoch_op` wraps an absolute bio index plus `disk_write`; `epoch` groups operations with metadata about barriers, overlaps, and checkpoint association; `EpochOpSector` represents a sub-bio sector view. `Permuter` exposes `InitDataVector()`, `GenerateCrashState()`, and `GenerateSectorCrashState()`, while requiring subclasses to implement `init_data()`, `gen_one_state()`, and `gen_one_sector_state()`.

Control flow and integration: `Tester` loads a `Permuter` from a shared object and calls the public generation methods. The public layer handles common preprocessing and uniqueness; subclasses decide which prefix/subset/sectors to keep.

State: private state is the epoch vector and completed-permutation set. `sector_size_` is protected for subclasses.

Dependencies: depends on `utils.h` disk-write structures and `PermuteTestResult` for logging generated states.

Risks: raw pointers in `EpochOpSector` refer into `epochs_`, so vector reallocation or stale sector objects can invalidate parents. The abstract `init_data()` hook exists but the base `InitDataVector()` does not call it in the current implementation, making it effectively dead unless subclasses are used differently.

Test signals: subclass conformance can be tested by loading `RandomPermuter.so` and verifying generated `DiskWriteData` reflects the epoch model.
