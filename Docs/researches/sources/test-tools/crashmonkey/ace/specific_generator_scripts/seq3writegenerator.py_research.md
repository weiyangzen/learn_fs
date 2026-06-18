# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3writegenerator.py

## Purpose

`seq3writegenerator.py` is a Python 2 workload enumerator focused on three-operation write/data-manipulation sequences. It searches combinations of buffered write, mmap write, fallocate, and direct write on `A/foo`, records whether they match a catalog of known filesystem crash bugs, and contains code to generate j-lang/C++ workloads for `code/tests/seq3write/`. In the checked-in version, most actual file emission is commented out, so it primarily logs and optionally matches bug workloads.

## Important APIs, Types, and Functions

- Search-space globals: `FileOptions = ['A/foo']`, `SecondFileOptions`, `DirOptions`, `SecondDirOptions`, `WriteOptions`, `dWriteOptions`, `TruncateOptions`, and `OperationSet = ['write', 'mmapwrite', 'falloc', 'dwrite']`.
- `expected_sequence` and `expected_sync_sequence` contain the same known-bug oracle catalog used by related generators.
- `buildTuple(command)` expands file/range/mode combinations. This variant uses larger 32 KiB append lengths, unaligned 5 KiB ranges, 8 KiB direct-write overlaps, and one primary file.
- `buildCustomTuple(file_list)` emits sync choices over the used files and includes both `fsync` and `fdatasync` plus `none`; global `sync` is intentionally commented out.
- Dependency helpers (`insertOpen`, `insertWrite`, `checkParentExistsDep`, `checkExistsDep`, `checkFileLength`, `satisfyDep`) are present to construct executable j-lang, though the generation block that uses them is currently commented.
- `buildJlang(op_list, length_map, mmaplist)` converts internal tuples into j-lang lines. It also records deferred `msync` operations for mmap writes in `mmaplist`.
- `doPermutation(perm)` filters candidate operation and parameter combinations, builds sync permutations, interleaves operation and sync/checkpoint tuples, and logs generated candidates.
- `main` initializes logging and globals, prints the bug catalog, constructs parameter lists, enumerates the operation products, and moves any generated `j-lang*` files into `code/tests/seq3write/j-lang-files/`.

## Control Flow

The intended pipeline is enumeration-first. `main` creates a log, builds all operation parameter choices, builds a general `SyncSet`, and calls `doPermutation` for each product of the active operation set. `doPermutation` skips all-write permutations, requires the first parameter tuple to contain `append`, rejects all-append sequences, computes the used file set, generates per-position sync permutations, and produces an interleaved `seq` list. If uncommented, the lower block would satisfy dependencies, write a j-lang file from `code/tests/seq3write/base-j-lang`, insert deferred `msync`/`munmap` before closing `Afoo`, invoke `workload_seq3.py`, and call `isBugWorkload`.

## State and Persistence Behavior

The persistent output actually guaranteed by current code is a timestamped `*-bugWorkloadGen.log`. The move command at the end may move any matching `j-lang*` files if they exist from a prior or partially uncommented run. The commented generation path would persist j-lang files and C++ generated tests in `code/tests/seq3write/`. Runtime state is stored in global counters and maps; range state during j-lang emission is stored in `length_map`, and mmap sync state is stored in `mmaplist`.

## Dependencies and Integration Points

This file uses Python 2 constructs and assumes it is run from the CrashMonkey repository layout where `code/tests/seq3write/base-j-lang`, `code/tests/seq3write/base.cpp`, and `workload_seq3.py` are reachable by relative path. Generated tests integrate with `workload_seq3.py`, the CrashMonkey C++ harness, and the Makefile's generated workload build rules if copied into a built test directory. Its j-lang commands overlap with `xfstestAdapter.py` translation semantics for `write`, `dwrite`, `mmapwrite`, `falloc`, `fsync`, and `fdatasync`.

## Risks and Edge Cases

- The script is Python 2 only and will fail directly under Python 3.
- Current file generation and bug matching are commented out in `doPermutation`, so the script may produce logs but no workloads.
- The final `mv j-lang* ...` can fail or move stale files unrelated to the current run.
- `elif option == 'overlap_unaligned_start' or ...` is always true for non-append options due to Python boolean semantics.
- `buildJlang` assumes `length_map[file]` exists for overlap/end/extend modes; that depends on the first command being append and on dependency insertion if generation is re-enabled.
- Direct I/O and mmap paths use fixed sizes and offsets; invalid alignment or insufficient file size would produce generated tests that fail before testing crash consistency.
- The one-file search space is useful for data-operation stress, but it misses cross-directory rename/link bugs represented in the shared oracle list.

## Test Signals

Signals include a log showing nonzero inspected workload counts, no accidental stale `j-lang*` movement, generated j-lang/C++ files if the commented block is intentionally enabled, successful `workload_seq3.py` translation, and generated tests that compile against the CrashMonkey harness. Runtime filesystem tests should verify append followed by unaligned fallocate, direct write overlap, mmapwrite plus deferred `msync`, and `fdatasync` versus `fsync` consistency expectations.
