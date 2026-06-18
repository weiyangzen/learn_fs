# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3generator.py

## Purpose

`seq3generator.py` is a legacy Python 2 sequence generator for longer, more constrained workload searches. It enumerates operation triples or quadruples over a reduced operation set and logs the resulting operation/parameter/persistence combinations. Unlike seq1 and seq2, the dependency-repair, J-lang emission, adapter invocation, and bug matching portions inside `doPermutation()` are commented out, so the active script primarily functions as a search-space/logging tool rather than a complete test generator.

## Important APIs, Types, and Functions

The seq3-specific operation domain narrows `FileOptions` to `B/foo` and `A/foo`, `SecondFileOptions` to `B/bar` and `A/bar`, `WriteOptions` to `append` and `overlap_unaligned`, `TruncateOptions` to `unaligned`, and `OperationSet` to `write`, `link`, `unlink`, `rename`, and `truncate`. The script still contains support code for other operations such as `creat`, `mkdir`, `mknod`, `falloc`, `dwrite`, `mmapwrite`, `fdatasync`, `fsetxattr`, `removexattr`, and `symlink`, but those are outside the active search set.

As in other ACE generators, `SiblingOf()`, `Parent()`, and `file_range()` describe the namespace. `buildTuple()` expands operation parameter domains. `buildCustomTuple()` supports sequence lengths 1 through 4, allowing `none` for non-final persistence points and requiring a real `fsync` or `sync` at the final point. `isBugWorkload()` is present but not called in the active path because the call is commented out.

The file includes the same insertion and dependency helpers as seq2: `insert*`, `check*`, `satisfyDep()`, `flatList()`, and `buildJlang()`. These functions remain available but are unreachable from the active `doPermutation()` body because the dependency-repair and output-generation block is commented out.

## Control Flow

`main()` opens a timestamped log, parses `--sequence_len`, prints the known bug catalog, fills `parameterList`, builds `SyncSet`, and loops over every operation skeleton in `itertools.product(OperationSet, repeat=int(num_ops))`.

`doPermutation()` skips skeletons where every operation is `write`, records the skeleton, expands parameter combinations, computes the used-file set, and deliberately chooses persistence points from `usedFiles` instead of `file_range(usedFiles)`. For each persistence choice, it interleaves core operations with sync/checkpoint metadata. `fdatasync` and `mmapwrite` are still treated as self-persisting, although they are not in the active `OperationSet`. The resulting `seq` is logged as the current sequence.

The code that would satisfy dependencies, copy `code/tests/seq3/base-j-lang`, emit J-lang, call an adapter, log the modified sequence, and run `isBugWorkload()` is commented out. `main()` also leaves the final move of generated `j-lang*` files commented. Therefore an active run produces logs and counters, but not test files.

## State and Persistence Behavior

The active persistent side effect is the timestamped `*-bugWorkloadGen.log`. The module-level counters and parameter maps track the number of skeletons and workload combinations inspected. Since generation is disabled, `global_count` counts logged persistence variants rather than generated files.

If the commented block were re-enabled, the script would use the same transient maps as seq2 to model open files, open directories, and file lengths, and would write J-lang/C++ tests under `code/tests/seq3/`.

## Dependencies and Integration Points

The active script only requires Python 2 and local filesystem access for the log. The inactive generation block references `code/tests/seq3/base-j-lang`, `code/tests/seq3/base.cpp`, and `workload_seq2.py` despite the seq3 target directory, suggesting the seq3 adapter integration was unfinished or copied from seq2. The generated J-lang command format is otherwise compatible with the older workload adapters.

## Risks and Test Signals

The biggest risk is that the script looks like a generator but does not currently emit tests. Any automation expecting `code/tests/seq3/` outputs from this file will silently receive only logs. The adapter command in the commented block calls `workload_seq2.py` for seq3 paths, which is suspicious if generation is restored. Like the other legacy scripts, it is Python 2-only, uses always-true option conditionals, and depends on global mutable counters.

Good validation signals include asserting that a run creates no J-lang files in its current form, checking logged `Total workloads inspected`, and, if generation is re-enabled, adding fixture tests around dependency repair for the `A`/`B` namespace and compiling generated seq3 C++ outputs. Tests should also decide whether persistence choices should use only `usedFiles` as the current code does or `file_range(usedFiles)` as comments and other generators often prefer.
