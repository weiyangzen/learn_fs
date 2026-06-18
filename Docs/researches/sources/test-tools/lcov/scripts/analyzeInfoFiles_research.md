# sources/test-tools/lcov/scripts/analyzeInfoFiles

Purpose: diagnostic Perl utility that compares multiple lcov `.info` traces for source-file presence, source version agreement, and per-line code/non-code consistency. It is intended for debugging inconsistent capture results from supposedly identical code bases.

Important APIs/types: defines internal `Region` objects with `start`, `finish`, `size`, `consistent`, `in`, `out`, `buildCodeKey`, and `print`; and `FileData` objects with `name`, `traces`, `regions`, `regionsBySize`, `totalRegionSize`, `print`, and `checkLineCoverageConsistency`. The executable interface accepts `--include`, `--exclude`, `--substitute`, `--keep-going`, `--drop`, `--all`, `--compact`, `--sort`, and `--verbose`.

Control flow and state: arguments are expanded from `.info` filenames or list files, then each `TraceFile->load` result is indexed by source path. For each source, the script checks version string equality across traces, detects missing source files, optionally drops missing files, then scans line numbers to group contiguous regions where info files disagree about whether a line is code. Global variables in package `main` carry options and file-index mappings into `Region`/`FileData`.

Dependencies and integration: loads `lcovutil` from adjacent lib paths and uses `TraceFile`, `TraceInfo->sum`, `keylist`, `value`, and lcov include/exclude/substitution pattern handling.

Risks and test signals: uses smartmatch (`~~`), shell `wc -l`, and source-file existence to set scan bounds. Missing files fall back to largest observed line number. It can produce false confidence if version callbacks are absent. Tests are indirect through generated `.info` fixtures, lcov merge/consistency tests, and manual diagnostic use.
