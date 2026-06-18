# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3nestedgenerator.py

## Purpose

`seq3nestedgenerator.py` is intended to enumerate ACE/CrashMonkey three-operation workloads over nested directory/file names, generate j-lang files under `code/tests/seq3-nested/`, and invoke a workload translator to produce C++ test cases. It specializes the broader sequence-generator idea for link/rename-heavy workloads on `A`, `B`, and nested `AC` paths. The checked-in file also embeds a catalog of known filesystem-crash bugs and expected operation/sync sequences, used as a sanity oracle by `isBugWorkload`.

## Important APIs, Types, and Functions

- Global option sets define the search space: `FallocOptions`, `FileOptions`, `SecondFileOptions`, `DirOptions`, `SecondDirOptions`, `WriteOptions`, `dWriteOptions`, `TruncateOptions`, and `OperationSet`. In this variant `OperationSet = ['link','rename']`, so most dependency and j-lang emission logic is broader than the active search.
- `expected_sequence` and `expected_sync_sequence` encode known bug-triggering command and sync patterns.
- `SiblingOf`, `Parent`, and `file_range` model the small synthetic namespace and compute related paths for sync/dependency candidates.
- `buildTuple(command)` expands an operation name into legal parameter tuples.
- `buildCustomTuple(file_list)` is intended to build per-position sync choices from used files, including `fsync`, `sync`, and `none`.
- `insert*` helpers create synthetic dependency operations and mutate `open_file_map`, `open_dir_map`, and `file_length_map`.
- `check*Dep` helpers enforce preconditions such as parent directory existence, file existence/open state, directory cleanup, xattr setup, and nonzero file length.
- `satisfyDep` walks a candidate sequence and injects setup/cleanup operations before unsafe commands.
- `buildJlang` converts internal operation tuples into j-lang text lines with concrete offsets and checkpoint commands.
- `doPermutation` enumerates operation permutations, filters disconnected parameter combinations, attaches sync permutations, satisfies dependencies, writes `j-langN`, and invokes `python workload_seq2.py`.
- `main` parses `--sequence_len`, logs generator statistics, populates parameter lists, iterates the operation product, and moves generated j-lang files into `code/tests/seq3-nested/j-lang-files/`.

## Control Flow

The intended flow is: parse sequence length, build parameter choices for the active operations, enumerate all length-N operation products, enumerate parameter products for each operation tuple, filter combinations that do not share a file/directory dependency, compute the set of used files, build sync choices for that used set, interleave operation and sync/checkpoint tuples, run dependency repair, emit a j-lang file, translate it with `workload_seq2.py`, and finally collect generated j-lang files.

For each candidate sequence, the dependency state machine keeps maps for open files, open directories, and file lengths. It uses these maps to insert parent `mkdir`, `open`, `close`, `unlink`, `rmdir`, and seed `write` operations so that the target command can execute in the generated C++ test harness. The j-lang emitter then maps path names like `A/foo` to flattened names such as `Afoo`, assigns append and overlap offsets, and adds `checkpoint 0/1` after sync operations.

## State and Persistence Behavior

State is mostly process-local mutable globals: `global_count`, `parameterList`, `SyncSet`, `syncPermutations`, `permutations`, `count`, `count_param`, and `log_file_handle`. Persistent side effects include timestamped `*-bugWorkloadGen.log` files, temporary `j-lang*` files in the current directory, generated C++ tests through the translator call, and a final `mv j-lang* code/tests/seq3-nested/j-lang-files/`. The generated workloads ultimately persist as files under the CrashMonkey test tree and become build inputs for the Makefile.

## Dependencies and Integration Points

This script depends on Python 2 syntax and modules (`xrange`, backtick repr, `print` statements, `string.maketrans`). It shells out to `workload_seq2.py` and assumes relative paths such as `code/tests/seq3-nested/base-j-lang` and `code/tests/seq3-nested/base.cpp` from the working directory. The output C++ tests depend on the ACE j-lang grammar understood by `workload_seq2.py`, CrashMonkey `BaseTestCase`, and the user tools/wrapper APIs compiled by `sources/test-tools/crashmonkey/code/Makefile`.

## Risks and Edge Cases

- The checked-in file appears syntactically invalid in several regions: indentation is broken around `buildCustomTuple`, `checkDirDep`, `checkParentExistsDep`, `checkExistsDep`, `satisfyDep`, `buildJlang`, `doPermutation`, and `main`. As stored, it is unlikely to run without manual repair.
- `elif option == 'overlap' or 'overlap_aligned' or 'overlap_unaligned'` is logically always true because nonempty string literals are truthy.
- The generator mutates dictionaries while iterating them when closing open files/directories, which is unsafe if Python notices size changes.
- Generated shell commands use relative paths and `shell=True`, so running outside the expected CrashMonkey root can write or move the wrong files.
- `min = 0` shadows the built-in `min`.
- `buildJlang` depends on `length_map[file]` being initialized for append fallocate, which may fail if dependency insertion did not seed the file.
- Active `OperationSet` only contains `link` and `rename`, while much of the bug catalog and implementation covers other operations, so coverage is narrower than the file name implies.

## Test Signals

Useful validation signals are: successful execution under Python 2 after indentation repair; a nonempty timestamped log with parameter and workload counts; generated `j-lang*` files under `code/tests/seq3-nested/j-lang-files/`; generated C++ files under `code/tests/seq3-nested/`; successful `make seq1` or an added target that builds these generated tests; and CrashMonkey runs that hit expected bug sequences reported by `isBugWorkload`. Negative tests should include running from a wrong working directory and malformed nested directory cases because path assumptions are strong.
