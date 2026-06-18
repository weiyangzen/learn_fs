# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_race_tools.h

## Purpose
Defines optional Valgrind DRD/Helgrind annotations and unsafe access helpers for the imported Toku code. When Valgrind support is unavailable, all annotations compile to no-ops so the locktree code can build normally.

## Important APIs, Types, And Functions
Macros include `TOKU_ANNOTATE_NEW_MEMORY`, `TOKU_VALGRIND_HG_ENABLE_CHECKING`, `TOKU_VALGRIND_HG_DISABLE_CHECKING`, `TOKU_DRD_IGNORE_VAR`, ignore-read/write begin/end annotations, and `TOKU_VALGRIND_RESET_MUTEX_ORDERING_INFO`. Templates `toku_unsafe_fetch` and `toku_unsafe_set` perform intentionally racy reads/writes while bracketing them with DRD ignore annotations.

## Control Flow
On Linux with `USE_VALGRIND`, the header includes Valgrind DRD and Helgrind headers and maps macros directly. Otherwise it defines `NVALGRIND`, sets `RUNNING_ON_VALGRIND` to zero, and turns the annotations into empty operations. Unsafe fetch/set execute a plain load or store while annotations are active; Helgrind enable/disable calls are compiled under `if (0)` due known false-positive behavior.

## State And Persistence Behavior
No persistent state is kept. The only side effects are tool annotations and the memory load/store in unsafe helpers.

## Dependencies And Integration Points
Used by OMT mark/index bitfields and other locktree internals that intentionally allow benign races. Integrates with DRD/Helgrind only in instrumented builds and is otherwise transparent to RocksDB.

## Risks And Edge Cases
These helpers can hide real races if used around mutable data without a higher-level synchronization argument. Because no-op mode is the default on most builds, correctness cannot depend on annotations. The `if (0)` Helgrind disable/enable blocks document a historical limitation but also mean Helgrind may still report some intentional races.

## Test Signals
Valgrind DRD runs should suppress known benign races around OMT mark bits. Ordinary unit tests only validate that the no-op path compiles and that higher-level concurrent lock operations behave correctly.
