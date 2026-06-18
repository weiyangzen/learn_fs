# Research: sources/test-tools/lcov/lib/lcovutil.pm

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009275`: lines 1-8021, `Docs/researches/chunks/subset-b-009275_research.md`
- `subset-b-009276`: lines 8022-10187, `Docs/researches/chunks/subset-b-009276_research.md`

## Chunk Research

### subset-b-009275: lines 1-8021

# sources/test-tools/lcov/lib/lcovutil.pm lines 1-8021

## Scope And Purpose

This chunk is the first and larger part of LCOV's shared Perl utility module. It defines package `lcovutil`, exports most shared command-line/configuration/error/filter helpers, and then defines the object model used to represent and manipulate LCOV trace data in memory. The covered range runs from module initialization through the beginning of `TraceFile::_filterFile`; it stops mid-filtering at line 8021, so the rest of per-line filtering, trace-file parsing, and trace-file writing belong to `subset-b-009276`.

At a high level, this code is the common runtime substrate for LCOV tools such as `lcov`, `geninfo`, and `genhtml`. It handles option and RC-file normalization, user-visible diagnostics, temporary files, optional callbacks, parallel child state merging, source-file lookup, source exclusion marker parsing, coverage filter selection, version/checksum validation, and the core in-memory representations for line, function, branch, and MC/DC coverage.

## Public Surface And Global Configuration

The module exports a large set of globals and helpers through `@EXPORT_OK`. Important exported values include tool metadata (`$tool_name`, `$tool_dir`, `$lcov_version`, `$lcov_url`), verbosity/debug state, temp directory tracking, RC parsing helpers, coverage-type booleans, filter identifiers and marker strings, file include/exclude/substitution pattern lists, error IDs, parallelism/memory knobs, callback configuration hooks, source/version/checksum controls, and color/palette maps used by report generation.

Many runtime switches are module-level global state rather than constructor-injected dependencies. Examples include `$br_coverage`, `$func_coverage`, `$mcdc_coverage`, `$case_insensitive`, `$stop_on_error`, `$treat_warning_as_error`, `$warn_once_per_file`, `$verify_checksum`, `$compute_file_version`, `$derive_function_end_line`, `$filter_blank_aggressive`, `$source_filter_lookahead`, and all filter histogram entries in `@cov_filter`. This makes initialization order important: callers are expected to run `define_errors`, `init_filters`, `parseOptions`, and related setup before loading or mutating trace data.

## Diagnostics, Errors, And Message State

`define_errors` assigns numeric IDs to all LCOV error names in `@lcovErrs`, populating `%lcovErrors`, `%ERROR_ID`, `%ERROR_NAME`, `@ignore`, `@message_count`, and `@expected_message_count`. `parse_ignore_errors` and `parse_expected_message_counts` consume comma-separated command-line/RC values and update suppression or expected-count state.

`ignorable_error` and `ignorable_warning` are the central reporting paths. They increment per-error counts, enforce `max_message_count`, record summary counters in `%message_types`, honor `--ignore-errors`, `--keep-going`/`stop_on_error`, and optionally convert warnings into errors. Fatal paths use `die_handler`; nonfatal paths use `warn_handler`. `_msg_handler` normalizes warning/error prefixes, optionally strips Perl source locations, can append stack traces when `LCOV_SHOW_LOCATION` requests developer detail, and writes to a message log under `flock` if configured.

`warn_once`, `store_deferred_message`, `merge_deferred_warnings`, and `explain_once` reduce duplicate diagnostics, especially in parallel mode. `summarize_messages` validates expected-count constraints and emits a compact summary of error, warning, and ignored message totals from the parent process.

Parallel child diagnostics are persisted through `initial_state`, `compute_update`, and `update_state`. A child records deltas for message counts, version/resolve caches, search-path use counts, pattern hit counts, callback save data, profile data, warning-once state, and explain-once state. The parent merges those deltas after child completion.

## Option And RC File Flow

`%rc_common`, `%geninfo_rc_opts`, and `%argCommon` define the shared configuration vocabulary. The code maps RC keys to scalar or array references, including filters, excludes/includes, source/build directories, callback scripts, checksum/version behavior, branch/function/MC/DC coverage toggles, message handling, parallelism, memory, color/filter behavior, and geninfo-specific knobs.

`read_config` reads `key = value` RC files, supports nested `config_file` inclusion with loop detection through `%included_config_files` and `@include_stack`, strips comments/whitespace, expands `$ENV{...}` at the start of values, rejects malformed lines, and skips unsupported keys for the current tool. Deprecated RC keys are collected as deferred diagnostics by `warnDeprecated`.

`apply_rc_params` does early pass-through parsing for `--config-file`, `--rc`, quiet/verbose/debug flags, loads user or default RC files, applies `--rc key=value` overrides, and updates language extension sets. `parseOptions` then combines shared and tool-specific `Getopt::Long` specs, handles help/version/message-log setup, merges RC-provided lists only when corresponding command-line lists are empty, creates source search paths, configures callbacks, checks callback-level/type values, initializes profiles, munges patterns, initializes parallel settings, parses expected message counts and filters, validates C++ demangling, and finally emits deferred RC diagnostics.

The option flow deliberately defers many errors until after ignore-error settings have been parsed. That is a useful behavior but also creates ordering risks: code that reports errors before `parse_ignore_errors` runs may be unavoidably fatal.

## Pattern, Filter, And Source Selection Helpers

`transform_pattern` converts shell-style file patterns into Perl regexes, respecting case-insensitive mode. `munge_file_patterns` converts include/exclude file patterns, compiles omit-line and exclude-function regexes, validates substitution expressions, validates exclusion marker regexes, and snapshots suppress-function patterns for later excessive-count suppression. `warn_file_patterns` reports unused include/exclude/substitute/omit/erase patterns and also invokes callback `finalize` methods late in a run.

Coverage filters are keyed by names such as `branch`, `brace`, `blank`, `directive`, `range`, `line`, `initializer`, `function`, `missing`, `region`, `branch_region`, `exception`, `orphan`, `mcdc`, and `trivial`. `init_filters` assigns their numeric IDs. `parse_cov_filters` enables requested filters and applies derived behavior: `line` enables brace and blank filtering; `branch` enables exception and orphan branch filtering; omit-line patterns create a synthetic `omit_lines` filter. `summarize_cov_filters` reports suppression histograms.

`skipCurrentFile` applies missing-file filtering, user exclude patterns, and include allowlists. File substitution is handled by `subst_file_name`; directory stripping by `strip_directories`; external-file detection by `is_external`.

## Callbacks, External Processes, And JSON/File IO

`configure_callback` supports two callback forms. A `.pm` callback module is loaded from its directory, instantiated with `Class->new`, and optionally registered for `save`/`restore`, `start`, and `finalize` lifecycle methods. Non-module callbacks are wrapped in `ScriptCaller`, which executes command-line scripts for version extraction, path resolution, context collection, annotation, criteria checking, name simplification, and history lookup.

`PipeHelper` owns a child pipe and normalizes close/error handling for callback scripts. `ScriptCaller` offers `call`, `pipe`, `context`, `extract_version`, `resolve`, `compare_version`, `annotate`, `check_criteria`, `select`, `simplify`, and `history`. These callbacks are integration points for source-control metadata, path resolution, report criteria, owner/date annotations, and custom coverage decisions.

`JsonSupport` dynamically selects a JSON module (`JSON::XS`, `Cpanel::JSON::XS`, `JSON::PP`, or `JSON`) unless overridden by RC. It provides `encode`, `decode`, and `load`. `InOutFile` abstracts input/output handles, stdin/stdout, gzip compression/decompression, and optional C++ demangling pipelines. `system_no_output` runs external commands through `Capture::Tiny` and controls stdout/stderr suppression or forwarding.

## Parallelism, Profiling, And Temporary State

`count_cores`, `read_proc_vmsize`, `read_system_memory`, `init_parallel_params`, and `current_process_size` implement parallelism and memory-throttle setup. The code can count Linux CPUs through `/proc/cpuinfo`, read total memory from `/proc/meminfo`, use `Memory::Process` if available, fall back to `/proc/self/stat`, and validate gzip availability when parallel intermediates are expected.

`create_temp_dir`, `append_tempdir`, and `temp_cleanup` manage temporary directories under `$tmp_dir`, with `$preserve_intermediates` disabling cleanup for debugging. `abort_handler` cleans temp dirs before exiting.

Profiling state lives in `%profileData`. `save_cmd_line` records command, tool binary path, and build directory. `merge_child_profile` merges nested profile hashes from parallel children, with special additive keys for known timing buckets. `save_profile` writes JSON profile data and, when requested for HTML output, creates HTML object wrappers for command-line and profile data.

## Version, Checksum, Dates, And Reporting Utilities

`extractFileVersion` calls a configured version callback once per source path, caches results in `%versionCache`, profiles callback time, and optionally checks file existence before invoking callbacks. `checkVersionMatch` first performs string equality, then delegates to `compare_version` if available, otherwise emits version mismatch diagnostics. `_merge_checksums` in `TraceInfo` merges per-line checksum data and reports mismatches.

`parse_w3cdtf` loads `DateTime::Format::W3CDTF` if available, otherwise parses common W3CDTF date forms into `DateTime` objects. `rate`, `get_overall_line`, `check_precision`, and `use_vanilla_color` support report summaries and coloring. `HTML_fileData` and `ValidateHTML` scan generated HTML files to find duplicate anchors, broken local links, invalid anchors, and unreferenced HTML pages.

## Coverage Criteria And Message Context

`CoverageCriteria` holds callback-driven pass/fail criteria. `executeCallback` calls a configured criteria callback with top/directory/file coverage data and records nonzero statuses or messages. `check_failUnder` converts built-in fail-under thresholds into top-level criteria failures. `summarize` prints all failed or message-bearing criteria and mirrors failures to stderr.

`MessageContext` is a small stack object. Constructing it pushes a text fragment; destruction asserts stack balance and pops it. Diagnostics call `MessageContext::context()` to append nested context such as "while loading" or "while filtering".

## Core Coverage Data Model

`MapData` is a thin hash wrapper used for checksum maps and per-testcase maps. `CountData` stores line-number-to-count data and cached found/hit totals. `append` validates numeric counts, reports non-integer, negative, or excessive counts, accumulates repeated keys, and updates found/hit counters. `union`, `intersect`, and `difference` implement tracefile merge operations for line coverage.

Branch coverage is represented by several layered types:

- `BranchElement` stores branch ID, taken count or `-`, optional expression, branch type (`VANILLA`, `EXCEPT`, `FALLTHROUGH`), exclusion state, and optional differential metadata.
- `BranchBlock` is an ordered list of branch elements with a signature string based on branch types.
- `BranchLocation` stores all branch blocks for one source line, indexed both by block order and by signature. It merges compatible blocks, clones new blocks, removes blocks, and computes found/hit totals.
- `BranchMap` tracks line-to-branch-location data and cached found/hit counts.
- `BranchData` extends `BranchMap` with block insertion, count recalculation, count consistency checks, and union/intersect/difference semantics.

MC/DC coverage has a similar model:

- `MCDC_Block` stores one line's MC/DC groups keyed by group size and validates expression compatibility.
- `MCDC_Expression` stores true/false sense counts and exclusion flags for one condition expression.
- `MCDC_Data` extends `BranchMap` with MC/DC append/creation, close-block count accumulation, recalculation, and union/intersect/difference operations.

Function coverage is represented by `FunctionEntry` and `FunctionMap`. `FunctionEntry` tracks a representative name, aliases, start/end lines, total hit count, and alias hit counts. It validates and accumulates alias counts, chooses a shorter non-lambda representative name, supports differential counts, finds line/branch/MC/DC coverpoints in its range, and removes aliases. `FunctionMap` indexes entries by start line and by alias name, detects duplicate names at different lines, reconciles mismatched end lines, counts functions/hits either per alias or merged under the function-alias filter, and implements union/intersect/difference operations.

`TraceInfo` is the per-source-file coverage container. It stores version, source location in the `.info` file, filename, checksums, line data, branch data, function data, and MC/DC data. Each coverage kind has both merged summary data and per-testcase maps. `TraceInfo::merge` selects the correct union/intersect/difference operations, checks version compatibility, merges testcase and summary data, and merges checksums.

## Source Loading And Exclusion Parsing

`ReadCurrentSource` resolves source paths through direct existence checks, source directories, substitutions, and optional resolve callbacks. `_load` reads the current source file and records its resolved path. `parseLines` scans all source lines and builds a per-line exclusion bitfield from LCOV markers and filters:

- line regions: `LCOV_EXCL_START`/`LCOV_EXCL_STOP`, `LCOV_EXCL_LINE`
- unreachable regions: `LCOV_UNREACHABLE_START`/`LCOV_UNREACHABLE_STOP`, `LCOV_UNREACHABLE_LINE`
- branch-only regions: `LCOV_EXCL_BR_START`/`LCOV_EXCL_BR_STOP`, `LCOV_EXCL_BR_LINE`
- exception-branch regions: `LCOV_EXCL_EXCEPTION_BR_START`/`LCOV_EXCL_EXCEPTION_BR_STOP`, `LCOV_EXCL_EXCEPTION_BR_LINE`
- C preprocessor directives when directive filtering is enabled
- user `omit-lines` regex matches

The parser reports overlapping, unmatched, and dangling exclusion markers. `isExcluded`, `excludeReason`, and `isOutOfRange` later use the exclusion bitfields to decide whether to suppress coverpoints, warn about out-of-range coverage data, or defer range diagnostics. Source heuristics such as `containsConditional`, `containsTrivialFunction`, `suppressCloseBrace`, `is_initializerList`, `isBlank`, and `isCharacter` support branch/brace/blank/trivial filtering. These heuristics intentionally err toward keeping coverage when uncertain.

## TraceFile Control Flow Covered In This Chunk

`TraceFile` is the top-level multi-file trace container. `load` constructs a new trace, creates a message context, reads an `.info` file through `_read_info` (defined later in the file, outside this chunk's visible implementation body), then applies filters. `new`, `serialize`, and `deserialize` create or persist the object through `Storable`.

Basic queries and mutation include `files`, `directories`, `file_exists`, `contains`, `data`, `insert`, `remove`, `comments`, and `add_comments`. `data` creates a `TraceInfo` lazily and supports case-insensitive keys and basename fallback for diff path matching. `count_totals`, `empty`, `print_summary`, `check_fail_under_criteria`, and `checkCoverageCriteria` aggregate line, branch, function, and MC/DC totals and run built-in or callback criteria.

`merge_tracefile` performs whole-trace union/intersect/difference by delegating per-file operations to `TraceInfo::merge`, removing missing files during intersection, adding new files during union, and preserving comments.

The filtering helpers visible in this chunk include:

- `_eraseFunction`, which removes line, branch, MC/DC, checksum, and function data for a function range.
- `_eraseFunctions`, which applies trivial-function and exclude-function filters, handles missing end-line cases, and reports hit functions marked unreachable.
- `_deriveFunctionEndLines`, which derives missing function end lines from sorted line coverage and neighboring function starts, propagates derived end lines to testcase function maps, records profile timing, and emits consistency diagnostics when derivation is impossible.
- `_fixFunction`, which adjusts summary and per-testcase function counts after ignored consistency errors when `fix_inconsistency` is enabled.
- `_checkConsistency`, which validates function hit state against contained line hit state, generates orphan MC/DC line data when needed, and checks branch/line consistency.
- `_filterFile`, whose beginning derives end lines, checks consistency, initializes active filter histograms, loads source for filtering, verifies source version compatibility, erases excluded/trivial functions, and then enters per-testcase filtering. This chunk stops immediately after fetching the first testcase's `CountData`.

## Branch Exception Filtering

`FilterBranchExceptions` encapsulates exception, orphan, region, and branch-region filtering. It removes exception branches and related fallthrough branches from both summary and per-testcase branch maps, updates filter histograms only on master data, removes empty branch blocks, and optionally removes orphan one-branch blocks. Its `filter` method uses `ReadCurrentSource::isExcluded` to decide whether a line is in a branch/exception/unreachable region and chooses the applicable histogram.

## State And Persistence Behavior

Most persistent runtime state is in global variables or mutable array/hash objects:

- Trace data persists in `TraceFile` -> `TraceInfo` -> `CountData`/`FunctionMap`/`BranchData`/`MCDC_Data`.
- Per-testcase data persists alongside summary data, and filters must mutate both to stay coherent.
- Pattern usage counts are stored in the last element of pattern arrays and are merged back from children.
- Message counts, suppression state, version/resolve caches, callback state, and profile state are global and explicitly merged in parallel mode.
- Temporary directories are tracked globally in `@temp_dirs`.
- Source-resolution search-path use counts persist in `SearchPath` instances and can be reported as unused options.
- Serialized tracefiles use Perl `Storable`, so object layout changes can affect compatibility with intermediates.

The code also writes optional persistent artifacts: profile JSON, profile HTML wrappers, command-line HTML wrappers, and message logs. Gzip-backed trace/intermediate IO goes through external `gzip`.

## Dependencies And Integration Points

This chunk depends on core Perl modules and several optional/external integrations: `File::Path`, `File::Basename`, `File::Temp`, `File::Spec`, `Scalar::Util`, `Cwd`, `Storable`, `Capture::Tiny`, `Module::Load::Conditional`, `Digest::MD5`, `FindBin`, `Getopt::Long`, `DateTime`, `Config`, `POSIX`, `Fcntl`, `Devel::StackTrace`, optional `Memory::Process`, optional `DateTime::Format::W3CDTF`, optional JSON modules, `gzip`, `c++filt` or a configured demangler, `/proc` on Linux, and user-supplied callback scripts/modules.

Internal integration points include the public LCOV executables that import this module, the later `TraceFile::_read_info` and write-info code in the same file, report-generation code that consumes palettes and TLA maps, callback modules implementing the documented callback methods, and merge/reconciliation code that expects union/intersect/difference behavior to preserve found/hit totals.

## Risks And Edge Cases

The main risk is global mutable state. Initialization order, child-process state merging, and repeated use in long-lived processes can affect diagnostics, filters, callbacks, pattern counts, caches, and profile data. Parallel mode adds extra hazards around callback save/restore correctness, fork failures, parent death, memory throttling, and duplicate warning suppression.

Source filtering is heuristic-heavy. Conditional detection, close-brace suppression, trivial-function detection, initializer-list filtering, and out-of-range handling can all produce false positives or false negatives for unusual C/C++ syntax, generated code, lambdas, macros, Perl branch data, or stale source/coverage version combinations.

Merge operations must preserve cached found/hit totals while mutating nested structures. Many methods clone blocks or remove elements while iterating; stale totals would corrupt summaries, fail-under criteria, and HTML report counts. The code includes `_checkCounts` and recalculation paths to catch some of this.

Callback execution and shell command construction are powerful integration surfaces. Script callbacks are invoked through shell-style command strings in several places, so paths/arguments containing spaces or shell metacharacters need careful handling by callers. Module callbacks can start child processes or maintain state; the code warns about unknown child processes and requires callback `save`/`restore` symmetry for parallel support.

Data validation intentionally turns malformed, negative, excessive, mismatched, or inconsistent coverage into LCOV diagnostics, and many diagnostics can be ignored. When ignored, the module often continues with repaired or synthetic data, such as clamping bad counts to zero, creating fake line data for branch/MC/DC consistency, or adjusting function counts.

## Test Signals

Useful tests for this chunk should exercise both normal and suppressed-error paths:

- RC and command-line parsing with config-file inclusion, deprecated keys, environment expansion, list/scalar options, `--rc` overrides, message logs, and quiet/verbose/debug interactions.
- Error handling with fatal errors, ignored errors, warning-as-error, max-message suppression, expected message-count constraints, deferred warnings, and child-state merging.
- Pattern handling for include/exclude/substitute/omit/erase patterns, invalid regexes, case-insensitive mode, unused-pattern warnings, and shell-wildcard conversion.
- Callback integration with script and module callbacks, including save/restore/start/finalize in parallel mode and callback failure diagnostics.
- JSON module selection, gzip input/output, demangle command validation, temp cleanup, profile output, and `/proc`/`Memory::Process` memory throttling fallback.
- Count, function, branch, and MC/DC data-model operations for append, remove, union, intersect, difference, duplicate/mismatched function definitions, branch signatures, excluded branches, differential metadata, and found/hit total recalculation.
- Source parsing with every LCOV exclusion marker, overlapping/unmatched regions, directive filtering, omit-line filtering, out-of-range lines, unreachable hit coverpoints, trivial functions, initializer lists, blank/brace suppression, and source version mismatches.
- TraceFile aggregation, merge_tracefile union/intersect/difference, fail-under criteria, callback criteria summaries, function end-line derivation, consistency checks, and the visible first phase of `_filterFile`.

The strongest regression signals are summary found/hit totals before and after filtering/merging, exact diagnostic types and counts, filter histogram counts, and consistency between summary data and per-testcase data after mutations.

### subset-b-009276: lines 8022-10187

# sources/test-tools/lcov/lib/lcovutil.pm lines 8022-10187

## Scope And Purpose

This chunk covers the tail of `TraceFile::_filterFile`, the parallel filter orchestration used by `TraceFile::applyFilters`, the `.info` reader and writer, and the `AggregateTraces` package that finds, loads, and merges tracefiles. It begins inside per-testcase source filtering and continues through module initialization.

The covered code is the late-stage normalization path for LCOV trace data. After earlier code has parsed options, built `TraceFile`/`TraceInfo` objects, loaded source files, derived function end lines, and prepared filter histograms, this chunk removes filtered function, branch, MC/DC, and line coverpoints; keeps summary and per-testcase data in sync; serializes child-process filter results; parses LCOV `.info` records into the in-memory model; writes the canonical `.info` format back out; and merges multiple input tracefiles, optionally in parallel.

## Main Control Flow

### Completing `TraceFile::_filterFile`

The chunk starts after `_filterFile` has fetched per-testcase maps from a `TraceInfo`:

- `testcount` is the current testcase's `CountData` for line records.
- `testfnccount`/`functionMap` hold function coverage for the testcase.
- `testbrcount` holds branch data, when branch coverage is enabled.
- `mcdc_count` holds testcase MC/DC data, when MC/DC coverage is enabled.
- Summary maps such as `$sumcount`, `$funcdata`, `$sumbrcount`, and `$mcdc` are shared across testcases and must be updated whenever a coverpoint is removed.

Function filtering first checks function start lines against source ranges and exclusion markers. If a function is out of range or excluded by a region/omit-line marker, the function key is removed from every testcase function map and from the summary `FunctionMap`. Unreachable regions are special: a hit function in an unreachable region reports `ERROR_UNREACHABLE` earlier in the filter path and can be retained when `$retainUnreachableCoverpointIfHit` is true.

Branch and MC/DC filtering then walks the union of testcase MC/DC lines and branch lines. It chooses one removal histogram based on out-of-range status, whole-line exclusion, branch-region exclusion, directive exclusion, omit-line exclusion, or the C branch-no-condition filter. When removal applies, the code removes both BRDA and MCDC data at that line from every testcase map and from the corresponding summary map, increments location and coverpoint counters, reports verbose filter messages, and recalculates branch counts. If the line is not otherwise removed, `FilterBranchExceptions->filter($line)` may mark/remove exception branches and orphan branch blocks.

The `mcdc_single` filter removes single-expression MC/DC blocks when there is a matching two-way branch expression on the same line. This treats such MC/DC entries as redundant with branch coverage and removes the testcase and summary MC/DC entry while incrementing the MC/DC-single filter histogram.

If `$excludeCoverpointCallback` is configured, `_filterFile` calls its `exclude($kind, $srcReader, $testCount, $sumCount)` method for `branch` and `mcdc`. Callback exceptions are reported through `ERROR_CALLBACK` but do not abort if that error is ignored.

Line filtering runs only when one of the relevant line-oriented filters is active. It skips lines that still have summary branch or testcase MC/DC data, because those lines are handled by branch/MC/DC filtering. Remaining DA lines can be removed for initializer-list ranges, out-of-range line numbers, exclusion/omit/directive markers, close-brace suppression, and blank-line suppression. Removed lines are deleted from every testcase line map, from the summary count map, and from checksum data. The function-alias filter histogram is updated at the end from the final summary function map counts.

### Parallel filtering

`TraceFile::applyFilters` computes a mask of work to perform: `DID_FILTER`, and optionally `DID_DERIVE` when function end-line derivation is enabled. It returns early when the tracefile state already includes the requested mask. Otherwise it iterates all files, removes skipped or external files, decides whether end-line derivation is needed, and builds a filter worklist for files that need source-based filters or function/trivial-function filtering.

`_processFilterWorklist` chooses serial or forked execution. Parallel mode is enabled when forced by `LCOV_FORCE_PARALLEL` or when there are more than 50 files, filter parallelism is enabled, and `$maxParallelism > 1`. It optionally honors `lcov_filter_chunk_size` as an absolute value or percentage, otherwise derives a chunk size from file count and parallelism. Work items are either single `[TraceInfo, name, actions]` entries for serial processing or chunk arrays for child processing.

For each child chunk, `_processParallelChunk` resets pattern/filter counters to per-child deltas, captures stdout/stderr with `Capture::Tiny`, calls `_filterFile` for each file in the chunk, records modified files, writes captured logs to temp files, and serializes updates, filter counters, warning state, timing state, and global child deltas through `Storable::store`.

The parent side uses `_mergeParallelChunk` to read child logs, retrieve serialized data, merge child message/profile/cache state with `lcovutil::update_state`, merge pattern and filter histogram counts, call `_updateModifiedFile` for each modified file, and record timing buckets such as `filt_undump`, `filt_merge`, `filt_queue`, and `filt_chunk`. Missing dump files or SIGKILL child exits are treated as retryable fork failures; the chunk is pushed back onto the worklist with retry counts. Other child failures are reported as parallel errors.

`_generate_end_line_message` emits a once-only GCC/gcov compatibility diagnostic when filtering had to deal with unsupported function end-line data. `_updateModifiedFile` writes the modified `TraceInfo` back into the `TraceFile` and calls that diagnostic helper if the shared state indicates unsupported end-line behavior was seen.

### Reading `.info` data

`TraceFile::_read_info($tracefile, $readSourceCallback, $verify_checksum)` parses an LCOV tracefile into the current `TraceFile`. It opens input through `InOutFile->in`, so compressed files and demangling pipelines are handled by that abstraction. It tracks current testcase, current source file, per-testcase maps, summary maps, current branch block, current MC/DC block, function index records, and whether the current file should be skipped by include/exclude/missing-file rules.

The parser recognizes:

- `TN:` testcase records, with non-word characters normalized to underscores unless testcase names are ignored globally.
- `SF:` and `KF:` source filename records, resolved through `ReadCurrentSource::resolve_path`; skipped files are logged once in `%excluded_files`.
- `VER:` source version records.
- `DA:` line coverage records, including optional checksum validation against the source file when checksums are enabled.
- Legacy `FN:` and `FNDA:` function records.
- Newer `FNL:` and `FNA:` function index/alias records.
- `BRDA:` branch records with optional type prefix `e` for exception and `f` for fallthrough, optional `U` unreachable/excluded marker, block id, branch id or expression, and taken count.
- `MCDC:` records with optional `U` marker, group size, true/false sense, count, expression index, and expression text.
- `end_of_record`, which finalizes current line/function/branch/MC/DC data into summaries and runs `TraceInfo::check_data`.

Branch parsing re-derives contiguous block IDs rather than trusting serialized IDs. It keeps one active `BranchBlock`; when the block id or source line changes, it inserts the previous block into the current testcase `BranchData` and starts a new block. Branch IDs can be arbitrary strings to support expression-oriented tools such as Verilog coverage emitters. Line number zero or negative branch records are reported as format errors but are retained if the error is ignored.

MC/DC parsing maintains one current `MCDC_Block` per line. When the line changes or the record ends, the current block is closed into summary MC/DC data and cloned into the current testcase MC/DC map. The parser preserves unreachable/excluded flags unless `$ignore_unreachable_flag` is set.

At `end_of_record`, line counts are unioned into summary counts, functions into summary function data when function coverage is enabled, branch blocks are inserted and count totals recalculated when branch coverage is enabled, MC/DC blocks are closed, and the file's internal consistency is checked. After the full file is read, empty files and empty testcase maps are removed. An empty tracefile after filtering/skipping reports `ERROR_EMPTY`.

### Writing `.info` data

`TraceFile::write_info_file($filename, $do_checksum)` opens an output handle through `InOutFile->out` and delegates to `write_info`. `write_info($handle, $verify_checksum)` emits the canonical `.info` format in stable sorted order.

For each source file and testcase, it writes `TN`, `SF`, optional `VER`, function records, branch records, MC/DC records, line records, summary count records, and `end_of_record`. The writer intentionally mirrors `_read_info`; comments in both functions warn that format changes must be kept synchronized and documented in `man/geninfo.1`.

Function output uses the newer indexed alias format. It sorts functions by start line and key, writes `FNL:<index>,<start>[,<end>]`, then writes one `FNA:<index>,<hit>,<alias>` for each alias. Function-found counts count merged functions, while function-hit counts count a function once if any alias is hit.

Branch output iterates branch lines numerically, then branch blocks in sorted/display order. It writes `BRDA:<line>,<type><U?><block>,<expr-or-id>,<taken>`. Excluded branch elements are serialized with `U` and are not included in `BRF`/`BRH` totals. MC/DC output emits two records per expression, one for true sense and one for false sense, with `U` when that sense is excluded; `MCF` counts both senses for each expression and `MCH` counts nonzero sense counts.

Line output writes DA records with optional checksums. If checksum verification is requested, existing checksum data is reused first; otherwise a `ReadCurrentSource` instance reads the current source and computes `Digest::MD5::md5_base64` for the line. `LF` and `LH` are recomputed from the testcase line map.

### Aggregate trace loading and merging

The `AggregateTraces` package is a shared utility for lcov add-trace behavior and genhtml multi-file ingestion.

`find_from_glob(@patterns)` expands input tracefile arguments. Direct files are accepted as-is. Patterns are glob-expanded, and directories are searched with `find '$dir' -name '$info_file_pattern' -type f`. Empty matches, unreadable files, and utility failures are reported through `ignorable_error`. The function returns the list of readable tracefiles to merge.

`_process_segment($total_trace, $readSourceFile, $segment)` processes a list of tracefiles sequentially inside one process. It skips missing or empty files, loads each file with `TraceFile->load($tracefile, $readSourceFile, $verify_checksum, 1)`, records parse and append profile timings, and either merges it into `$total_trace` with `TraceInfo::UNION` or, when `$function_mapping` is enabled, builds a map from unique function location to function name and tracefiles that hit it. In normal merge mode, files that improve coverage are returned as "interesting" inputs for pruning/reporting.

`merge($readSourceFile?, @tracefiles)` is the public aggregate entry point. It accepts an optional `ReadCurrentSource` or `ReadBaselineSource`; without an object it constructs `ReadCurrentSource` for backward compatibility. It temporarily disables source-based coverage filters while reading input tracefiles, because parsing source for each input is expensive and filtering is applied once after merging. It initializes parallel settings and optionally reduces `$maxParallelism` based on `$maxMemory`, current process size, and largest input file size.

If parallelism is available and there are multiple inputs or `LCOV_FORCE_PARALLEL` is set, `merge` partitions the sorted or original file list into segments, forks one child per segment up to the segment count, captures child output, serializes each child result through `Storable`, and merges child results in the parent. Child failures from missing dump files or SIGKILL are retried by pushing the segment back to the queue; other failures are reported as child/parallel errors. In sequential mode it simply calls `_process_segment` once.

After all segments are merged, `merge` removes the configured temp directory when appropriate, re-enables the previously disabled coverage filters, calls `$total_trace->applyFilters($readSourceFile)`, and returns `($total_trace, \@effective)`.

## Important APIs And Types

- `TraceFile::_filterFile($traceInfo, $source_file, $actions, $srcReader, $state)`: mutates one file's coverage data according to active filters and returns the updated `TraceInfo` plus a modified flag.
- `TraceFile::_processFilterWorklist($srcReader, $fileList)`: serial/parallel driver for file-level filtering.
- `TraceFile::_processParallelChunk(...)`: child-process filter worker; emits logs and serialized updates.
- `TraceFile::_mergeParallelChunk(...)`: parent-process merge path for child filter results.
- `TraceFile::applyFilters($srcReader?)`: public idempotent entry point for derivation and source-based filtering.
- `TraceFile::is_language($lang_expr, $filename)`: extension-based language predicate, where `$lang_expr` can be pipe-separated.
- `TraceFile::_read_info($tracefile, $readSourceCallback, $verify_checksum)`: parser for LCOV `.info` files.
- `TraceFile::write_info_file($filename, $do_checksum)` and `TraceFile::write_info($handle, $verify_checksum)`: `.info` output writers.
- `AggregateTraces::find_from_glob(@patterns)`: expands user-supplied tracefile inputs and directories.
- `AggregateTraces::_process_segment($total_trace, $readSourceFile, $segment)`: sequential parser/merger for one segment.
- `AggregateTraces::merge($readSourceFile?, @tracefiles)`: high-level multi-input merge with optional parallelism and post-merge filtering.

The main data types used here are the structures defined earlier in the same module: `TraceFile`, `TraceInfo`, `CountData`, `FunctionMap`, `FunctionEntry`, `BranchData`, `BranchBlock`, `BranchElement`, `MCDC_Data`, `MCDC_Block`, `MapData`, `ReadCurrentSource`, `ReadBaselineSource`, `FilterBranchExceptions`, `InOutFile`, and `MessageContext`.

## State And Persistence Behavior

Filtering mutates both per-testcase and summary data. Removing a function, branch, MC/DC block, or line from only one layer would leave output summaries inconsistent, so most removal paths explicitly iterate all testcase maps and then remove from the summary map. Branch removals call `updateCounts` to refresh cached found/hit totals.

Filter and pattern histograms are mutable global arrays in `@lcovutil::cov_filter`, `@exclude_function_patterns`, and `@omit_line_patterns`. Parallel filter children zero those counters, record only local deltas, serialize the deltas, and the parent adds them back. Warning counts, callback state, source-resolution caches, version caches, and profile data are also process-local in children and are reconciled through `lcovutil::compute_update`/`update_state`.

Temporary persistence uses files in a temp directory:

- Filter children write `filter_$$.log`, `filter_$$.err`, and `dumper_$$`.
- Aggregate children write `lcov_$$.log`, `lcov_$$.err`, and `dumper_$$`.
- Serialized child payloads use Perl `Storable`, so object layout and Perl-version compatibility matter for parallel intermediates.

Tracefile persistence is the LCOV `.info` text format. This chunk is both reader and writer for that format, so any new record type or field must be implemented symmetrically. Checksums are persisted in DA records when configured. Source versions are persisted in `VER:` records. Excluded/unreachable branch and MC/DC senses are persisted through `U` markers.

`TraceFile` state bits `DID_FILTER` and `DID_DERIVE` make `applyFilters` idempotent. `AggregateTraces::merge` deliberately disables filters during input parsing and applies them after all input is merged, changing when source-related diagnostics and filter histogram counts are produced.

## Dependencies And Integration Points

This chunk depends on global configuration and helpers from package `lcovutil`, including coverage enable flags, filter definitions, include/exclude patterns, warning/error reporters, profile data, memory/parallelism settings, temp-directory settings, checksum/version settings, and callback objects.

Important internal integration points include:

- `ReadCurrentSource` and `ReadBaselineSource` for source loading, exclusion markers, checksum lines, language-specific heuristics, and diff-aware baseline reconstruction.
- `FilterBranchExceptions` for exception/orphan branch removal from summary and testcase branch maps.
- `TraceInfo::get_info`, `TraceInfo::check_data`, and coverage data-model operations such as `union`, `remove`, `insertBlock`, `updateCounts`, `append_mcdc`, and `close_mcdcBlock`.
- `InOutFile` for stdin/stdout, gzip input/output, demangle pipelines, and safe file-handle ownership.
- `Capture::Tiny`, `fork`, `wait`, `POSIX::SIGKILL`, `File::Temp`, `File::Spec`, and `Storable` for parallel execution.
- `Digest::MD5` for DA checksum validation and generation.
- External `find` in `AggregateTraces::find_from_glob` when an input pattern resolves to a directory.
- User callbacks, especially `$excludeCoverpointCallback`, version callbacks used before filtering, and callback save/restore state merged from children.

The major user-facing integration is with tools that load or write `.info` files, especially `lcov` add/remove/extract flows and `genhtml` report generation. `genhtml` calls `AggregateTraces::merge`, then consumes the filtered `TraceFile` data to build summaries and source views.

## Risks And Edge Cases

The highest-risk area is keeping nested coverage maps coherent while filtering. Many operations delete from all testcase maps and the summary map, but MC/DC single-expression filtering assumes `$mcdc_count` and `$testbrcount` are defined. That path is gated by the filter flag, but tests should cover files with MC/DC enabled and no corresponding branch data to guard against undef dereferences.

Parallel filtering and aggregate merging rely on temp dump files named by child PID. Missing dump files and SIGKILL are retried, but serialization failures, child output races, stale temp dirs, or ignored parallel errors can leave partially merged state. The code also mutates global `$maxParallelism` when applying memory throttling, which can affect later work in a long-lived process.

`AggregateTraces::find_from_glob` builds a shell `find` command using single-quoted directory and filename-pattern strings. Paths or patterns containing embedded single quotes are risky. It also splits `find` stdout on whitespace, so discovered filenames containing whitespace can be broken into multiple entries.

The `.info` parser is permissive when errors are ignored. Invalid line numbers, checksum mismatches, duplicate or unknown function indexes, unexpected record formats, and malformed branch/MC/DC records may continue into the in-memory model. This is useful for "keep going" behavior but makes downstream consistency checks and writer validation important.

Parser/writer symmetry is fragile. Branch type markers, `U` exclusion markers, function alias indexes, MC/DC true/false sense records, checksum fields, and summary count records must remain compatible with external LCOV producers and older LCOV consumers. New fields need updates in `_read_info`, `write_info`, and manual documentation together.

Source filtering is source-version sensitive. `_filterFile` skips source-based filtering when the current source version differs from the tracefile's recorded version, but checksum verification and range/exclusion filtering depend on the source reader being opened to the correct current or baseline reconstruction. Misconfigured version callbacks can therefore suppress filtering or produce stale checksum diagnostics.

Global mutable state affects repeatability. Testcase name normalization, ignored testcase names, branch/function/MC/DC enable flags, omit/exclude patterns, `ignore_unreachable_flag`, `exclude_exception_branch`, and filter histograms all alter parse or filter behavior. Parallel child merging must preserve these effects without double-counting diagnostics or filter counters.

## Test Signals

Strong regression tests for this chunk should check exact `.info` round trips and summary totals:

- Filtered functions are removed from every testcase `FunctionMap` and from summary `FunctionMap`, with alias histograms reflecting final merged/alias counts.
- Out-of-range, excluded, directive, omit-line, no-conditional branch, exception branch, orphan branch, and MC/DC-single filters update the right histograms and leave branch/MC/DC found/hit totals consistent.
- Unreachable hit coverpoints produce `ERROR_UNREACHABLE` and are retained or removed according to `$retainUnreachableCoverpointIfHit`.
- Line filtering skips lines that still own branch or MC/DC data, removes DA/checksum records from all relevant maps, and handles initializer-list, close-brace, blank-line, range, directive, region, and omit filters.
- Serial and parallel `applyFilters` produce identical trace data, diagnostics, filter histograms, and profile keys for the same input corpus.
- Parallel filter and aggregate paths retry SIGKILL/missing-dump failures and report non-retryable child errors without silently losing chunks.
- `_read_info` accepts legacy `FN`/`FNDA` and indexed `FNL`/`FNA` functions, branch records with vanilla/exception/fallthrough types and expression IDs, MC/DC true/false records, version records, checksum records, comments, empty lines, and ignored summary records.
- `write_info` output can be parsed back into equivalent `TraceFile` data, including function aliases, function end lines, branch excluded flags, MC/DC excluded senses, and optional line checksums.
- Checksum verification reports missing/mismatched checksums and recomputes checksums on write when source is available.
- `AggregateTraces::merge` yields the same merged `TraceFile` sequentially and in parallel, preserves effective/interesting input lists, handles `function_mapping` mode, disables filters during parse, and applies filters once after merge.
- `find_from_glob` covers direct files, globs, directories containing `.info` files, empty matches, unreadable matches, and filenames with spaces or other shell-sensitive characters.
