# sources/test-tools/lcov/bin/geninfo

## Purpose

`geninfo` is the LCOV capture engine for GCC/gcov-style coverage artifacts. It scans one or more data/build directories for `.gcda` and `.gcno` files, runs a selected `gcov` tool, parses either classic `.gcov` text output or gcov intermediate text/JSON output, and emits LCOV `.info` trace data. It is also responsible for initial zero-coverage capture from `.gcno` files, include/exclude filtering, source-path normalization, checksum/version/comment metadata, branch/function/MC/DC collection when supported, and parallel processing of large coverage sets.

The script is a command-line tool but relies heavily on the shared `lcovutil` library for option parsing, trace-file data structures, filtering, diagnostics, profile output, and coverage criteria checks.

## Important APIs, types, and functions

- Command options are collected in `%geninfo_opts` and merged with `lcovutil::geninfo_rc_opts` through `lcovutil::parseOptions()`. Important options include `--output-filename`, `--base-directory`, `--gcov-tool`, `--initial`, `--all`, `--compat`, `--no-recursion`, `--external`/`--no-external`, `--large-file`, and inherited filter/checksum/coverage options.
- Compatibility state is represented by `%compat_value` with modes for `libtool`, `hammer`, and `split_crc`. `parse_compat_modes()` validates names and values, applies defaults, and supports delayed or automatic mode detection.
- `IntervalMonitor` reports periodic processing progress and child CPU time.
- `BuildWorkList` owns discovery of `.gcda`/`.gcno` work items. `find_files()` shells out to `find`; `add_worklist_entry()` de-duplicates files; `find_corresponding_gcno_file()` locates matching graph files beside `.gcda` files, under configured build directories, or through resolve callbacks.
- `gen_info()` builds the work list, divides it into chunks, handles serial and forked child processing, merges child `Storable` dumps, and updates profiling counters.
- `_process_one_chunk()` and `_merge_one_child()` are the parallel-processing glue. Children write temporary LCOV/Storable data under the temporary directory and parent processes merge it into `TraceFile` state.
- `process_dafile()` is the classic gcov path for a single data/graph pair. It reads `.gcno`, invokes `gcov`, resolves generated `.gcov` files back to source files, populates `TraceFile` entries, and deletes intermediates unless preservation is requested.
- `read_gcov_file()` parses classic `.gcov` content into line, branch, and function maps. It handles branch blocks, exception/fallthrough annotations, unexecuted block markers, demangling, and duplicate instance lines.
- `process_intermediate()`, `read_intermediate_text()`, `read_intermediate_json()`, `intermediate_text_to_info()`, and `intermediate_json_to_info()` implement the gcov `-i` intermediate-format path.
- `read_gcno()` and helpers (`read_gcno_word()`, `read_gcno_value()`, `read_gcno_string()`, `read_gcno_lines_record()`, `read_gcno_function_record()`) parse binary graph files to find source files, instrumented lines, and function declarations.
- Path helpers such as `solve_relative_path()`, `compute_internal_directories()`, `match_filename()`, `solve_ambiguous_match()`, `adjust_source_filenames()`, and `filter_source_files()` normalize source/build paths and enforce include/exclude/external rules.

## Control flow

At startup the tool installs LCOV warning/die handlers, forces `LC_ALL=C` so gcov output is parseable, parses command-line and rc options, validates the `gcov` executable, detects the gcov version and supported flags, decides whether intermediate format should be used, builds the final gcov command line, and normalizes data directories.

The main capture flow is:

1. Validate directories/globs and compute internal directories used by `--no-external`.
2. Create or select a temporary directory for child data and gcov intermediates.
3. Call `gen_info()` for all input directories.
4. `BuildWorkList` finds `.gcda` files for normal capture, `.gcno` files for `--initial`, or both for `--all`.
5. Work is chunked. Large files and chunk zero are handled serially; other chunks may be processed by forked children subject to `--parallel` and memory limits.
6. Each data item either creates zero-count initial coverage from graph data or executes gcov, parses generated coverage, and returns `TraceFile` data.
7. Parent and child results are merged; source filters and coverage filters are applied.
8. A single output trace is written when `--output-filename` is set. Without a single output file, per-input outputs are emitted as processing occurs.
9. Summaries, warnings, profile data, and coverage criteria status are reported before process exit.

For classic gcov output, `process_dafile()` changes into a temporary directory, invokes gcov with `-o` pointing at the object directory, reads each generated `.gcov` file, matches it against source entries from `.gcno`, and populates line/function/branch maps. For intermediate output, gcov's generated `.gcov`/JSON data is loaded directly and converted to LCOV records without reparsing source-looking text files.

## State and persistence behavior

Persistent output is LCOV `.info` data written to `--output-filename`, stdout, or generated per-file outputs depending on options. Temporary state is written under `File::Temp` or configured `--tempdir`; children serialize merge state with `Storable` and may write captured stdout/stderr logs. Temporary `.gcov` files and child info files are removed unless `--preserve`/`preserve_intermediates` is set.

In-memory state is global-heavy: `@gcov_tool`, `$gcov_version`, `$gcov_caps`, `@data_directory`, `$trace_data`, `%compat_value`, `$single_file`, `$files_created`, profile hashes in `lcovutil`, and package-level counters. Child workers inherit this state across `fork()` and return deltas to the parent.

The script also changes process state: it sets locale, changes directories while running gcov, installs signal handlers, and may follow symlinks when computing internal source directories.

## Dependencies and integration points

`geninfo` depends on core Perl modules (`File::Basename`, `File::Spec`, `File::Temp`, `File::Copy`, `File::Path`, `Cwd`, `Capture::Tiny`, `Storable`, `POSIX`, `Time::HiRes`) and on `sources/test-tools/lcov/lib/lcovutil.pm`. External integration points are the selected `gcov` executable, `find`, optional demangling/version/context/resolve scripts, source files referenced by gcov output, and the filesystem layout of build/data directories.

It is invoked directly by users and indirectly by `lcov --capture`, which passes through many options and marks the call with `--call-from-lcov`. Its output is consumed by `lcov`, `genhtml`, and other LCOV trace readers.

## Risks and edge cases

- The tool shells out to `find`, `gcov`, optional scripts, and demanglers. Quoting and unusual filenames remain a high-risk area, especially with spaces, shell metacharacters, symlinks, and Windows/MSYS paths.
- Global mutable state plus `fork()` makes parallel failures subtle. Child serialization, partial temp cleanup, parent death checks, and retry behavior must stay aligned.
- Source-path matching is inherently heuristic when gcov emits relative paths or multiple source files share the same basename. `solve_ambiguous_match()` can fail if source text is unavailable or generated content differs.
- Version-dependent gcov formats are complex. GCC 9+ text format is deliberately rejected in favor of intermediate output, while JSON/intermediate parsing has separate assumptions.
- `read_gcno()` is a hand-written binary parser. Incorrect length, endianness, artificial-function, or version handling can drop functions or misassign line coverage.
- `--initial` cannot produce branch coverage in some modes, and branch/function/MC/DC flags depend on gcov capabilities detected from `gcov --help`.
- Filtering happens in multiple phases: source file filtering, exclusion markers, coverage filters, function erasure, and external filtering. Ordering bugs can change reported totals.
- Temporary links are created when data and graph files are in different directories; interrupted runs or preserve mode can leave artifacts.

## Test signals

Useful tests include invoking `geninfo --help` and `--version`, normal capture against a tiny GCC-instrumented C/C++ fixture, `--initial` capture from `.gcno`, `--all`, `--base-directory`, `--build-directory`, `--no-external`, include/exclude filters, branch/function coverage, and gcov intermediate JSON/text paths. Regression coverage should include duplicate basenames, symlinked build directories, libtool `.libs` layouts, missing `.gcno`, empty `.gcda`, child parallel processing, `--parallel 1` versus multiple workers, and malformed gcov/gcno inputs that should produce ignorable errors. Output should be validated with `lcov --list`, `genhtml`, and checksum/coverage-criteria checks.
