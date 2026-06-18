# sources/test-tools/crashmonkey/ace/ace.py

## Purpose

`ace.py` is the main Python 3 entry point for Automatic Crash Explorer workload generation. It exhaustively enumerates filesystem operation skeletons of a requested sequence length, expands each skeleton into concrete file/path/range/options combinations, inserts persistence points (`fsync`, `fdatasync`, `sync`, or `none`), repairs preconditions by injecting setup operations, emits J-lang or J2-lang workload files, and invokes either the CrashMonkey C++ adapter or the xfstest adapter to produce runnable tests under `../code/tests/seq*`.

The file also embeds a catalog of expected bug-reproduction signatures in `expected_sequence` and `expected_sync_sequence`. These signatures are used by `isBugWorkload()` as a sanity signal that the generator's search space includes known crash-consistency bugs.

## Important APIs, Types, and Functions

The file is procedural and uses module-level globals rather than classes for generator state. `build_parser()` defines CLI options for sequence length, nested test namespace, demo mode, and test backend. `print_setup()` prints those parsed values.

`SiblingOf()`, `Parent()`, and `file_range()` encode the small synthetic namespace model used by ACE. They map logical J-lang names such as `foo`, `A/foo`, `B/bar`, `AC/foo`, and `test` to sibling and parent choices so persistence operations can be limited to relevant files and directories.

`buildTuple(command, expand_combinations=True)` is the operation-domain builder. It returns all legal parameter tuples for core operations such as `creat`, `mkdir`, `falloc`, `write`, `dwrite`, `mmapwrite`, `link`, `rename`, `unlink`, `remove`, `fsetxattr`, `removexattr`, `truncate`, `fsync`, and `fdatasync`. With `expand_combinations=False`, it returns parameter dimensions for the concise J2-lang path.

`buildCustomTuple(file_list)` builds per-position persistence sequences from the files touched by a workload. It ensures the last operation is followed by a real persistence point for the active sequence length, while allowing `none` before earlier operations. `isBugWorkload()` compares generated operations, parameters, and persistence choices against the known bug catalog and logs matches.

The dependency-injection layer is split between tuple constructors (`insertUnlink()`, `insertRmdir()`, `insertXattr()`, `insertOpen()`, `insertMkdir()`, `insertClose()`, `insertWrite()`) and checkers (`checkCreatDep()`, `checkDirDep()`, `checkParentExistsDep()`, `checkExistsDep()`, `checkClosed()`, `checkXattr()`, `checkFileLength()`). `satisfyDep()` is the central dispatcher that mutates `modified_sequence` and state maps for each operation.

`flatList()` normalizes nested tuple/list command records. `buildJlang()` converts dependency-expanded tuples into the older J-lang text format, including offsets, lengths, and checkpoint return values. `buildJ2lang()` emits the newer grouped J2-lang format for concise xfstests. `doPermutation()` is the full CrashMonkey/xfstest generation path, while `doPermutationV2()` is the concise xfstest-only path. `SlowBar` customizes progress display with the global workload count.

## Control Flow

`main()` opens a timestamped `*-bugWorkloadGen.log`, parses arguments, validates `--test-type`, mutates global operation domains for demo and nested modes, and builds `parameterList` for every operation in `OperationSet`. It then prepares output directories under `../code/tests/seq<num_ops>[_nested][_demo]`, copies `ace-base` templates, initializes persistence operation choices, and iterates `itertools.product(OperationSet, repeat=int(num_ops))`.

For normal CrashMonkey or xfstest generation, each operation skeleton is handed to `doPermutation()`. That function skips all-write length-3 skeletons, records the skeleton, computes the cartesian product of operation parameters, prunes length-3 parameter combinations that do not reuse files, computes the used-file set, chooses persistence combinations, then interleaves each core operation with its selected persistence point. Operations that are themselves persistence-producing (`fdatasync` and `mmapwrite`) skip an extra inserted sync and receive checkpoint return metadata directly.

After skeleton, parameter, and persistence enumeration, `doPermutation()` performs dependency repair. It starts with `open_dir_map = {'test': 0}` and empty file length/open maps, walks the current sequence through `satisfyDep()`, inserts required parent-directory creation, opens, closes, unlinks, writes, xattr setup, and directory cleanup, then closes any remaining open handles. The repaired sequence is serialized to a temporary `j-lang<global_count>` file copied from `base-j-lang`, and then converted by `cmAdapter.py` or `xfstestAdapter.py` through `subprocess.call()`.

For `--test-type xfstest-concise`, `main()` routes skeletons to `doPermutationV2()`. That path currently intends to support only sequence length 1, builds J2-lang from unexpanded parameter dimensions, and invokes `xfstestAdapter.py` with a zero-padded test number.

## State and Persistence Behavior

The generator relies heavily on mutable module globals: `global_count`, `parameterList`, `SyncSet`, `num_ops`, `nested`, `demo`, `syncPermutations`, `count`, `permutations`, `log_file_handle`, and `count_param`. Per-workload transient state is held in `open_file_map`, `open_dir_map`, and `file_length_map`. These maps model logical existence/open state and byte lengths so generated workloads have satisfiable preconditions and deterministic offsets.

Persistent side effects are substantial. The script writes timestamped logs in the current working directory, creates or updates `../code/tests/seq*` directories, copies base J-lang and C++ skeletons, writes many temporary `j-lang*` or `j2-lang*` files, invokes adapter scripts that create `.cpp` tests, and finally moves generated high-level language files into `../code/tests/seq*/j-lang-files/`. It does not maintain a database or durable manifest beyond generated files and logs.

## Dependencies and Integration Points

`ace.py` imports operation domains from `common.py`, uses `progress.bar.FillingCirclesBar` for status, uses `shutil.copyfile` for template copying, and shells out to `cmAdapter.py` and `xfstestAdapter.py`. It assumes a specific directory layout relative to the ACE working directory: `../code/tests/ace-base/base-j-lang`, `../code/tests/ace-base/base.cpp`, and destination directories under `../code/tests/seq*`.

The integration contract with adapters is textual J-lang/J2-lang. `buildJlang()` emits commands such as `open`, `opendir`, `mkdir`, `mknod`, `falloc`, `write`, `dwrite`, `mmapwrite`, `link`, `rename`, `unlink`, `remove`, `fsetxattr`, `removexattr`, `truncate`, `fsync`, `fdatasync`, `sync`, and `checkpoint`. The CrashMonkey adapter expects checkpoint lines to contain a return value that identifies the final crash point.

## Risks and Test Signals

The boolean parsing is fragile: `parsed_args.nested == ('True' or 'true')` and the demo equivalent only compare against `"True"`, not `"true"`. `SecondFileOptions` and `SecondDirOptions` are extended with `AC/bar` and `AC` outside the `if nested` block, so non-nested runs still receive some nested targets. Several option checks use expressions such as `elif option == 'overlap' or 'overlap_aligned' or 'overlap_unaligned'`, which are always true after the first false comparison. `doPermutationV2()` checks `len(num_ops) != 1`, which tests the length of the string instead of the numeric sequence length. Shell command strings are built with concatenation and `shell=True`; current arguments are internally generated or CLI-provided paths, so injection and quoting risks exist.

State is global and not concurrency-safe. The commented multiprocessing code correctly notes that enabling parallel generation would collide on `global_count` and output file names. The generator also mutates imported lists from `common.py`, so repeated runs inside the same interpreter would be unsafe.

Useful test signals include running short demo generations, verifying known bug matches printed by `isBugWorkload()`, checking that generated `j-lang-files/` counts match logged `global_count`, and compiling or running the generated CrashMonkey/xfstest outputs. Unit tests should isolate `buildTuple()`, `buildCustomTuple()`, `Parent()`, `SiblingOf()`, `buildJlang()`, and dependency checkers for representative file, directory, xattr, rename, and direct-write workloads.
