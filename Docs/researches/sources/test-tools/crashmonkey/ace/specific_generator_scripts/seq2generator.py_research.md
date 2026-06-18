# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq2generator.py

## Purpose

`seq2generator.py` is a legacy Python 2 workload generator specialized around length-2 ACE searches. It enumerates pairs of filesystem operations, fills in concrete parameters, inserts persistence choices after each operation, injects dependency operations, emits J-lang files, and calls a seq2 adapter wrapper to create CrashMonkey tests under `code/tests/seq2/`.

## Important APIs, Types, and Functions

The file duplicates most constants and functions from the later `ace.py`, but with seq2-specific defaults. `OperationSet` includes `creat`, `mkdir`, `falloc`, `write`, `dwrite`, `link`, `unlink`, `remove`, `rename`, `removexattr`, `fdatasync`, `fsetxattr`, `truncate`, and `mmapwrite`; `symlink` and `mknod` are intentionally removed in this version. The expected bug catalog is extended with comments through 29 known or desired sequences, while concrete `expected_sequence` entries cover the first 13 signatures.

`buildTuple()` returns parameter combinations for each operation. For `link`, `symlink`, and `rename`, seq2 allows first operands from both first and second file options, reducing missed cases where the second operation reuses a previously created target. `buildCustomTuple()` returns persistence sequences tailored to sequence length: for length 2 it allows `fsync`, `sync`, or `none` after the first operation, and only `fsync` or `sync` after the last operation.

The state-repair helpers (`insertUnlink()`, `insertRmdir()`, `insertXattr()`, `insertOpen()`, `insertMkdir()`, `insertClose()`, `insertWrite()`, `checkCreatDep()`, `checkDirDep()`, `checkParentExistsDep()`, `checkExistsDep()`, `checkClosed()`, `checkXattr()`, `checkFileLength()`, and `satisfyDep()`) model file existence, directory existence, open handles, and minimum file length. `flatList()` and `buildJlang()` turn the repaired tuple sequence into J-lang text with checkpoint return values.

## Control Flow

`main()` opens a log, parses `--sequence_len`, prints known bug definitions, populates `parameterList`, initializes `SyncSet`, and iterates all `OperationSet ** num_ops` operation skeletons. Although intended for seq2, it accepts any sequence length supported by `buildCustomTuple()`.

`doPermutation()` records each skeleton, builds the cartesian product of parameter choices, flattens the current parameter tuple to compute `usedFiles`, and chooses persistence targets from `file_range(usedFiles)`. For each persistence combination, it interleaves core operations with persistence operations. `fdatasync` and `mmapwrite` are treated as self-persisting and receive checkpoint metadata directly instead of a following sync operation.

The initial sequence is dependency-expanded using `satisfyDep()`, with `test` preloaded as an existing closed directory. Remaining open files and directories are closed. The script copies `code/tests/seq2/base-j-lang`, appends a `# run` section, writes the repaired J-lang commands, and invokes `python workload_seq2.py -b code/tests/seq2/base.cpp -t <j-lang> -p code/tests/seq2/ -o <global_count>`. At completion it moves `j-lang*` into `code/tests/seq2/j-lang-files/`.

## State and Persistence Behavior

State is held in Python 2 module globals (`global_count`, `parameterList`, `SyncSet`, `num_ops`, `syncPermutations`, `count`, `permutations`, `log_file_handle`, `count_param`) and transient per-workload maps (`open_file_map`, `open_dir_map`, `file_length_map`). Persistent outputs include the timestamped log, generated J-lang files, generated C++ tests, and the final moved J-lang archive. There is no manifest or atomic output handling.

## Dependencies and Integration Points

The script depends on Python 2 and the seq2-specific wrapper `workload_seq2.py`. It assumes the repository is run from a directory where `code/tests/seq2/base-j-lang`, `code/tests/seq2/base.cpp`, and `code/tests/seq2/j-lang-files/` are valid. The generated J-lang command set must be accepted by the workload adapter and the CrashMonkey C++ skeleton.

## Risks and Test Signals

The script carries the same always-true write-option conditional as seq1 and ACE. It relies on string splitting and tuple flattening, which can mis-handle malformed operation tuples. `isFadatasync` is set but not used for pruning after assignment. `checkDirDep()` deeply special-cases directory `A` contents and does not generalize to every namespace in comments. Generated command execution uses `shell=True` and non-quoted paths.

Useful tests include verifying that known seq2 bug signatures are reachable, checking that final persistence choices never end in `none`, compiling generated seq2 C++, and comparing generated workloads for representative pairs such as `link/unlink`, `write/falloc`, `rename/creat`, `fsetxattr/removexattr`, `truncate/write`, and `mmapwrite/link`.
