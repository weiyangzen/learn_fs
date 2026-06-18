# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq1generator.py

## Purpose

`seq1generator.py` is a legacy Python 2 generator specialized for sequence length 1 workloads. It predates the consolidated Python 3 `ace.py` path and duplicates much of the same search-space, dependency-repair, J-lang emission, and CrashMonkey adapter invocation logic. Its output target is `code/tests/seq1/`.

## Important APIs, Types, and Functions

The file defines operation-domain globals inline: fallocate modes, sync operations, first/second file sets, directories, write/direct-write/sync-range/truncate options, and an `OperationSet` that includes `creat`, `mkdir`, `mknod`, `falloc`, `write`, `dwrite`, `link`, `unlink`, `remove`, `rename`, `symlink`, `removexattr`, `fdatasync`, and `fsetxattr`.

`expected_sequence` and `expected_sync_sequence` encode 13 known bug signatures. `isBugWorkload()` logs when a generated sequence matches one of those signatures. `SiblingOf()`, `Parent()`, and `file_range()` implement the logical namespace for `foo`, `bar`, `A/foo`, `A/bar`, `A`, `B`, and `test`.

`buildTuple()` expands one operation into all concrete parameter choices. It supports legacy-only `syncrange` as well as `mmapwrite`, even though those are not currently active in `OperationSet`. `buildCustomTuple()` builds persistence choices for the used file range, but unlike the newer `ace.py` it does not include `none` in the default sync set for sequence length 1.

The dependency layer mirrors ACE: tuple insertion helpers create synthetic operations, `check*` functions enforce existence/open/length/xattr/parent preconditions, `satisfyDep()` dispatches by command, and `buildJlang()` serializes tuple commands to J-lang. `doPermutation()` handles one operation skeleton through parameter expansion, sync insertion, dependency repair, file writing, adapter execution, and bug matching.

## Control Flow

`main()` opens a timestamped log, parses `--sequence_len`, prints all known bug signatures, populates `parameterList`, initializes `SyncSet`, and iterates `itertools.product(OperationSet, repeat=int(num_ops))`. Although the script is named for seq1, it still accepts arbitrary `--sequence_len`; its output paths and workload adapter remain hard-coded to seq1.

`doPermutation()` receives a tuple such as `('write',)`, gets parameter combinations for the operation, computes used files from the selected parameters, expands persistence choices over `file_range(usedFiles)`, and special-cases `fdatasync`, `mmapwrite`, and `syncrange` so they do not receive an extra persistence command. It builds an initial sequence `[core_op_with_params, sync_choice]`, then runs dependency repair over that sequence.

The repaired sequence is appended to a copied `code/tests/seq1/base-j-lang` template. Each generated J-lang file is converted by calling `python workload_seq1.py -b code/tests/seq1/base.cpp -t <j-lang> -p code/tests/seq1/ -o <global_count>`. At the end, all generated `j-lang*` files are moved into `code/tests/seq1/j-lang-files/`.

## State and Persistence Behavior

The script uses Python 2 globals for counters, parameter lists, persistence sets, and logging. Per-workload state is maintained in maps for open files, open directories, and file lengths. The script writes a timestamped log, many `j-lang*` files in the working directory, generated C++ tests under `code/tests/seq1/`, and finally moves high-level language files into the seq1 `j-lang-files` directory.

## Dependencies and Integration Points

This script requires Python 2 syntax and modules, including backtick repr syntax, `print` statements, `xrange`, `basestring`, and `from string import maketrans`. It shells out to `workload_seq1.py`, which is the seq1-specific adapter wrapper in the same folder. It assumes `code/tests/seq1/base-j-lang`, `code/tests/seq1/base.cpp`, and `code/tests/seq1/j-lang-files/` exist relative to the current working directory.

## Risks and Test Signals

The script is not Python 3 compatible. Its command generation is hard-coded to seq1 paths even when `--sequence_len` is not 1. Several conditions are logically faulty, including `elif option == 'overlap' or 'overlap_aligned' or 'overlap_unaligned'`, which always triggers the file-length branch for non-append writes. The `remove`/`unlink` dependency path uses `current_sequence[pos][1][0]` in this file, which can reduce a string filename to its first character for some sequence shapes.

Like `ace.py`, it uses global counters and would collide if multiprocessing were enabled. It also builds shell commands with concatenated paths and `shell=True`. Good validation signals are a very small seq1 generation run, successful conversion through `workload_seq1.py`, generated C++ compilation, expected known-bug match output, and fixture tests for `buildJlang()` offsets for append, aligned overlap, unaligned overlap, truncation, sync-range, and mmapwrite.
