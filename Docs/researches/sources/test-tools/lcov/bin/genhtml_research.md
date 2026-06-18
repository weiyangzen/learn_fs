# Research: sources/test-tools/lcov/bin/genhtml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009271`: lines 1-7224, `Docs/researches/chunks/subset-b-009271_research.md`
- `subset-b-009272`: lines 7225-14230, `Docs/researches/chunks/subset-b-009272_research.md`

## Chunk Research

### subset-b-009271: lines 1-7224

# sources/test-tools/lcov/bin/genhtml lines 1-7224

## Scope and Purpose

This chunk is the front half of the `genhtml` Perl executable from LCOV. It starts with program metadata, imports, global defaults, function prototypes, and then defines the bulk of the in-memory model used to convert LCOV trace data into differential HTML report data. The line range ends in `main` while command-line and lcovrc option tables are being assembled; the actual option parsing and most HTML writer implementations continue in later lines.

The central purpose of this chunk is to build report-ready coverage summaries from current trace data, optional baseline trace data, optional unified diff data, optional source annotations, and optional callbacks. It categorizes coverpoints into LCOV differential TLAs such as `UNC`, `GNC`, `LBC`, `CBC`, `DUB`, and `DCB`; builds per-file, per-directory, per-owner, and per-age-bin summaries; loads or synthesizes source lines; and schedules file/directory/top-level report generation serially or through forked child jobs.

## Major Packages and Responsibilities

### Script Setup and Global State

- The script imports standard Perl modules for filesystem work, process state, timing, serialization, cloning, path handling, and dates: `File::Basename`, `File::Path`, `File::Spec`, `File::Temp`, `Cwd`, `DateTime`, `Date::Parse`, `Storable`, `POSIX`, and others.
- It imports LCOV-local behavior from `lcovutil`, including tool metadata, warning/error handling, parsing helpers, coverage flags, precision/rate helpers, path filtering, and callback/error constants.
- Global defaults define report thresholds, image/navigation sizes, field widths, sort modes, header modes, HTML settings, source-view behavior, differential display flags, and scheduler debugging.
- The first-line prototypes declare the HTML writer and data-processing functions that are implemented later in the file, including `gen_html`, `process_file`, `write_summary_pages`, `write_source`, `write_file_table`, and `write_function_table`.
- `main` state begins near the end of this chunk: current/base trace objects, `DiffMap`, path prefix options, report titles, output directory, baseline/diff settings, owner/date display flags, source synthesis, hierarchy/flat-view mode, HTML extension/gzip state, function alias behavior, and lcovrc/CLI option maps.

### `SummaryInfo`

`SummaryInfo` is the main aggregate data structure for top-level, directory, and file summaries. Instances are array-backed objects whose slots hold type/name/parent/path metadata plus coverage data for lines, branches, MC/DC, and functions.

Important behavior:

- Defines the differential TLA ordering, display titles, legacy mappings, default date cutpoints, owner-table truncation controls, and compact summary-table defaults.
- `_initCounts()` initializes count buckets for `found`, `hit`, and all supported TLAs.
- `noBaseline()` switches display semantics to the simplified `GNC`/`UNC` model when no baseline is available.
- `setAgeGroups()` sorts date-bin cutpoints, validates optional labels, creates default labels, and builds `ageHeaderToBin`.
- `new()` creates file, directory, or top-level records and preallocates age bins when annotation is enabled.
- `append()` merges child summaries into parent summaries, including normal count totals, per-age buckets, and per-owner buckets for each supported coverage type.
- Accessors and counters such as `get`, `get_rate`, `get_missed`, `lineCovCount`, `branchCovCount`, `mcdcCovCount`, and `functionCovCount` provide uniform summary arithmetic.
- Owner/date helpers such as `owners`, `owner_tlaCount`, `findOwnerList`, `hasOwnerInfo`, and `hasDateInfo` drive owner and age-bin detail tables.
- `removeLine()` backs out summary counts when select filtering drops a line from a source view.
- `checkCoverageCriteria()` packages summary data into callback input, including optional date and owner details, then invokes `CoverageCriteria::executeCallback`.

### Detail Callback Classes

Several small classes normalize how later HTML table code asks for coverage counts:

- `OwnerDetailCallback` returns owner-specific counts for a selected coverage type.
- `DateDetailCallback` returns age-bin-specific counts.
- `FileOrDirectoryCallback` returns total coverage data and destination links for files/directories.
- `FileOrDirectoryOwnerCallback` and `FileOrDirectoryDateCallback` provide secondary table rows grouped by owner or age bin and can enumerate matching files.
- `CovTypeSummaryCallback` adapts a `SummaryInfo` instance for branch, MC/DC, or function totals.
- `PrintCallback` tracks the current TLA, owner, age, and next navigation positions while rendering source lines.

These classes are integration glue between the data model in this chunk and the HTML writer functions defined later.

### `LineData` and `FileCoverageInfo`

`LineData` represents one logical source line across baseline/current versions. It stores old and current line numbers, line hit counts, branch data, MC/DC data, function data, and the resulting differential TLA. Deleted lines use synthetic string keys like `<<<123` and store the closest current-line leader as a negative line number.

`FileCoverageInfo` creates a per-file differential coverage map from current trace data, optional baseline trace data, and a `DiffMap`.

Key categorization behavior:

- `_categorize()` maps baseline/current hit counts to baseline TLAs: `UBC`, `GBC`, `LBC`, `CBC`, or excluded-current TLAs `EUC`/`ECC`.
- `_categorizeIfExcluded()` handles no-baseline/current-only cloning with excluded coverpoints.
- `_categorizeLineCov()` walks current line coverage, then baseline line coverage, aligns lines through `DiffMap`, marks inserted/deleted/equal lines, records deleted-line regions, and assigns line TLAs.
- `_categorizeBranchCov()` aligns branch blocks by line and code, preserving baseline/current counts in cloned branch elements. Inserted/current-only branches become `UNC`/`GNC`; deleted branches become `DUB`/`DCB`; current-only branch blocks on unchanged lines become `UIC`/`GIC`; missing current blocks on unchanged lines become `EUB`/`ECB`.
- `_categorizeMcdcCov()` performs similar logic for MC/DC expression groups and both boolean senses.
- `_categorizeFunctionCov()` aligns functions by leader line, clones function entries, stores differential function entries in `functionMap`, handles aliases, and uses known function end lines to recategorize unchanged functions with changed bodies as new-code TLAs where appropriate.
- `recategorizeTlaAsBaseline()` rewrites `UIC`/`GIC` into `UBC`/`CBC` for old files newly added to coverage, including line, branch, MC/DC, and function data.

The categorization logic is intentionally tolerant of inconsistent trace/diff data. Many inconsistencies are reported through `lcovutil::ignorable_error`, allowing configured `--ignore-errors` behavior to continue.

### `DiffMap`

`DiffMap` parses and queries unified diff data.

Important behavior:

- Stores `LINEMAP` chunks keyed by current filename, `FILEMAP` mappings from current to baseline names, captured deleted baseline lines, diff file locations, unchanged-file markers, symlink aliases, and the diff root.
- `load()` reads unified diff data and optionally scans build directories for symlink aliases that can reconcile source paths.
- `_read_udiff()` parses:
  - `Git Root: ...` records.
  - `=== file` unchanged records.
  - `--- old` and `+++ new` filename records.
  - `@@ -old,count +new,count @@` hunk headers.
  - space, `-`, `+`, and empty content lines.
- `lookup()` maps a line number from old to new or new to old.
- `type()` returns whether a line is `EQUAL`, `INSERT`, or `DELETE`, falling back to identity/equal/insert behavior when no diff was loaded.
- `recreateBaseline()` rebuilds baseline source text from current source plus deleted lines captured from the diff.
- `find_deleted_line_leader()` and `compute_deleted_lines()` map deleted baseline regions to current source anchors for source-view navigation.
- `check_version_match()` and `check_path_consistency()` compare diff paths and versions against baseline/current trace files, including basename-mismatch diagnostics and optional `elide_path_mismatch` repair.

### Source Loading and Annotation

`ReadBaselineSource` extends `ReadCurrentSource` so baseline source can be reconstructed from current source plus `DiffMap` when needed.

`SourceLine` is a line-level record containing line number, text, owner abbreviation/full name, date, age, commit id, and attached line/branch/MC/DC/function TLA data.

`SourceFile` is the per-source-file detail model used by source views and navigation:

- `_load()` resolves paths, checks optional file versions, invokes annotation callbacks when configured, falls back to file reads, and optionally synthesizes missing source content.
- `_computeAge()` computes line age in days from annotation timestamps, honoring `SOURCE_DATE_EPOCH` for reproducible report generation and warning when annotation time is in the future.
- `_synthesize()` pads missing source lines from coverage data and function end lines, optionally adding synthetic annotation metadata.
- `_bare_load()` reads real source lines into `SourceLine` records.
- The constructor loads/synthesizes lines, optionally recategorizes old newly-covered files as baseline, applies select filtering with `InInterestingRegion`, counts line/branch/MC/DC/function TLAs into `SummaryInfo`, and records owner/category line lists for navigation.
- `simplify()` drops most source-detail data after file-page generation when running in parallel and when the full serializable database is not needed.
- Navigation helpers such as `nextTlaGroup`, `nextCategoryTlaGroup`, `nextInDateBin`, `nextInOwnerBin`, `nextBranchInDateBin`, `nextMcdcInDateBin`, `nextBranchInOwnerBin`, and `nextMcdcInOwnerBin` find the next line matching category/owner/date filters.

`InInterestingRegion` supports select callbacks by expanding selected code coverpoints with contiguous matching non-code lines plus configurable context lines.

### `TestcaseTlaCount`

`TestcaseTlaCount` stores per-testcase counts for line, branch, MC/DC, or function coverage. In normal mode it records `found` and `hit`; with TLA display enabled and `SourceFile` details available, it also counts hit coverpoints by differential TLA. Function handling respects `merge_function_aliases`.

### `GenHtml` Scheduler

`GenHtml` orchestrates report computation across files, directories, and the top-level summary.

Control flow:

1. `new()` creates the top-level `SummaryInfo`, builds pending dependency records, orders files using optional profile-history predictions, creates directory records for hierarchical or legacy two-level layout, and adds file tasks to the worklist.
2. `compute()` repeatedly segments ready work, runs jobs serially or forks child workers, waits for children when parallelism or memory limits require it, and finishes when no jobs/work/pending dependencies remain.
3. `_segment_worklist()` groups ready tasks into job segments based on available parallelism and `max_tasks_per_core`, creates output directories unless HTML generation is disabled, and computes relative/base/truncated directory names.
4. `compute_one()` dispatches a single file, directory, or top-level task to `main::process_file()` or `main::write_summary_pages()`, then runs coverage criteria checks and optionally shrinks file details.
5. `merge_one()` merges completed file/directory/top summaries into their parent and clears dependency entries.
6. `_process_child()` captures child stdout/stderr, runs assigned tasks, serializes task results and lcovutil state deltas to a temp `Storable` file, and returns an exit status.
7. `_waitChild()` and `merge_child()` reap children, restore serialized results, replay output, merge summaries, update criteria/profile state, detect missing or corrupt dumps, and reschedule jobs after recoverable child failures.
8. `_reschedule()` and `_report_fail_and_reschedule()` restore task directory state and retry jobs after fork/child/serialization problems.

Persistent scheduler state is written under a `File::Temp->newdir("genhtml_XXXX", DIR => $lcovutil::tmp_dir, CLEANUP => 1)` directory with files named like `genhtml_$pid.log`, `genhtml_$pid.err`, and `dumper_$pid`.

## State and Persistence Behavior

- Most objects are array-backed Perl objects with numeric slot constants. This is compact and serialization-friendly, but makes slot ordering part of the internal ABI.
- Top, directory, and file summaries form a tree through `SummaryInfo` parent/source links. In parallel children, parent/source references are cleared before serialization to reduce dump size.
- Coverage counts are held in hashes keyed by `found`, `hit`, and TLA names. Age bins and owner bins are merged upward from file to directory to top-level summaries.
- Source details can be discarded or simplified after HTML generation to reduce memory. `buildSerializableDatabase`, `show_details`, `no_sourceview`, `frames`, and `show_tla` determine how much survives.
- Diff parsing persists deleted baseline text so baseline source can be reconstructed for source reads and deleted-code display.
- Annotation and version/profile/criteria callback effects are tracked in global lcovutil state and per-package counters; child processes serialize deltas for the parent to merge.
- Output side effects in this range are mostly scheduler temp files, output directory creation, optional empty-directory cleanup, diagnostics to stdout/stderr, and updates to global profile timing data. Actual HTML/CSS/image writing functions are mostly outside this chunk.

## Dependencies and Integration Points

- LCOV internal modules and classes: `lcovutil`, `TraceFile`, `TraceInfo`, `CountData`, `BranchLocation`, `BranchBlock`, `BranchElement`, `MCDC_Block`, `FunctionEntry`, `ReadCurrentSource`, `InOutFile`, `CoverageCriteria`, `MessageContext`, and `Capture::Tiny`. Many are defined in LCOV library files, not this script chunk.
- External callbacks: annotate callbacks, select callbacks, coverage criteria callbacks, version extraction callbacks, simplify-function callbacks, and profile-history callbacks.
- Filesystem integration: source reads, diff reads, output directory creation, symlink alias scanning, temporary directory/dump/log files, source path realpath/abs path normalization, and case-insensitive path mode.
- Process integration: `fork`, `wait`, `waitpid(WNOHANG)`, POSIX signal status, per-child stdout/stderr capture, and `Storable` serialization across fork boundaries.
- Reproducibility integration: `SOURCE_DATE_EPOCH` affects age calculations for annotation and synthetic lines.
- Later-script integration: this chunk prepares data consumed by `process_file`, `write_summary_pages`, source HTML writers, table writers, CLI parsing, and final report generation implemented after line 7224.

## Control Flow Notes

- Current trace data drives the initial file worklist. Baseline trace and diff data are optional but change TLA assignment substantially.
- No-baseline reports default to `GNC`/`UNC`; baseline reports classify unchanged, inserted, deleted, gained, lost, included, and excluded coverpoints.
- Line coverage is categorized first and establishes the `LineData` map that branch, MC/DC, and function coverage attach to.
- Source annotation is optional. Without it, owner/date bins are absent, but core line/branch/function totals still work.
- Select filtering happens after source load and before final TLA counting. Dropped lines are removed from `SummaryInfo` totals.
- Directory and top-level summaries are only scheduled after their dependencies complete.
- Parallel jobs are used only when `lcovutil::maxParallelism > 1` and there is enough work to justify fork overhead. Memory limits can force waits before scheduling more children.

## Risks and Edge Cases

- Array-backed objects are fragile: adding or reordering constants can corrupt serialized data and object interpretation.
- `LineData::curr_count()` appears to add to an undefined slot in the first-assignment branch (`$linecov->[LINE_CURRENT] += $inc`), relying on Perl's numeric undef coercion and warning behavior.
- Several comparisons mix numeric and string semantics. Deleted-line keys like `<<<123` require custom sort/compare handling and are easy to mishandle in future code.
- Diff parser support is tailored to unified diffs and custom `=== unchanged`/`Git Root` records. Nonstandard hunk headers, binary diffs, renames without expected headers, paths with unusual escaping, or filenames equal to `/dev/null` require careful testing.
- `_findChunk()` is a bespoke binary search over overlapping insert/delete/equal ranges. Boundary lines around hunks and insert/delete anchors are high-risk.
- `DiffMap::check_path_consistency()` can mutate mappings under `elide_path_mismatch`; false positives could associate coverage with the wrong same-basename file.
- Branch and MC/DC categorization assumes stable block/expression ordering between baseline and current for matching structures. Compiler or instrumentation changes can turn logical matches into apparent deletions/insertions.
- Function categorization by leader line and alias maps can be misleading when functions move, split, merge, or have unstable end-line metadata.
- Annotation callbacks must return consistent all-commit or all-no-commit data per file; mixed results are fatal.
- Future annotation timestamps relative to `SOURCE_DATE_EPOCH` or current time trigger inconsistent-data handling and collapse age to zero.
- Missing or short source files can be synthesized, which keeps report generation alive but can hide real path/configuration problems unless source/range errors are treated strictly.
- Parallel child serialization depends on `Storable` successfully dumping reduced objects. Large `SourceFile` details, circular references, callback state, or unexpected object contents can create memory pressure or serialization failures.
- Child stdout/stderr are slurped fully into memory during merge. Very verbose child output can increase parent memory use.
- `merge_child()` reschedules missing dump files and SIGKILL failures, but other child failures report parallel errors and may rely on broader `lcovutil` keep-going behavior.
- The option map includes a likely typo key, `genhtml_show_havigation`, which may be intentional compatibility or a configuration spelling bug.

## Test Signals

- Differential line coverage tests should cover no-baseline, unchanged hit/miss, gained/lost coverage, inserted hit/miss, deleted hit/miss, excluded current coverpoints, and files newly added to coverage with `treatNewFileAsBaseline`/age-base behavior.
- Branch and MC/DC tests should cover matching blocks/groups, current-only blocks, baseline-only blocks, excluded current elements, missing line coverage for branch/MC/DC lines, and unstable ordering.
- Function tests should cover aliases, merged-vs-unmerged alias reporting, known/unknown end lines, body changes with unchanged leader lines, deleted functions, inserted functions, and functions present without executable line data.
- Diff tests should exercise path stripping, `Git Root`, `=== unchanged`, `/dev/null` new/deleted files, hunk boundary lookups, deleted-line leaders, path mismatch elision, case-insensitive mode, symlink aliases, and empty diffs.
- Source loading tests should cover real readable sources, missing files with and without synthesis, files shorter than coverage ranges, CRLF stripping, version script mismatches, and baseline reconstruction from diff data.
- Annotation tests should cover valid owner/date/commit data, no-commit files, mixed commit/no-commit error handling, future timestamps, `SOURCE_DATE_EPOCH`, missing owner fields, callback exceptions, and nonzero callback exit statuses.
- Select callback tests should verify selected-code filtering, non-code contiguous expansion, context-line inclusion, and summary count removal for filtered-out lines.
- Owner/date table tests should validate age-bin boundaries, custom label mismatches, owner truncation, all-vs-missed filtering, and branch/MC/DC owner navigation.
- Scheduler tests should cover serial mode, parallel mode, dependency ordering, hierarchical and flat views, fork failure rescheduling, SIGKILL/OOM rescheduling, missing/corrupt dump files, child diagnostics replay, max-memory throttling, and empty-directory cleanup.
- Configuration tests should cover lcovrc and CLI bindings introduced in this chunk, including source view, frames, gzip, precision, coverage thresholds by type, dark mode, hierarchy/flat mode, annotation/select/simplify callbacks, date bins/labels, owner table controls, and source synthesis.

## Cross-Chunk Notes

- The prototypes at the top refer to many functions implemented after this chunk, including the main HTML writing functions and `process_file`.
- The chunk starts at executable initialization and ends while `%genhtml_options` is still being populated; actual option parsing, validation, trace loading, and final report-generation entry flow continue after line 7224.
- Many referenced LCOV data classes (`TraceFile`, `CountData`, branch/MC/DC/function structures, callback wrappers) are external to this script or defined outside this line range.

### subset-b-009272: lines 7225-14230

# sources/test-tools/lcov/bin/genhtml lines 7225-14230

## Scope

This chunk covers the second half of the `genhtml` script. It starts in the top-level command-line option table and includes option normalization, trace ingestion orchestration, output asset creation, all major HTML renderer helpers, source-code view rendering, owner/date/differential navigation tables, function table generation, and late utility routines. Earlier packages in the same file define the data objects consumed here, including `SummaryInfo`, `FileOrDirectoryCallback`, `FileOrDirectoryOwnerCallback`, `FileOrDirectoryDateCallback`, `FileCoverageInfo`, `SourceFile`, `PrintCallback`, and `GenHtml`.

## Purpose

The covered code is the report-generation backend for lcov trace data. It turns parsed command-line and rc options into global rendering state, merges current and optional baseline traces, applies optional unified diff data, builds source and summary objects, and writes a tree of HTML, CSS, PNG, gzip, frameset, description, source, directory, file, owner/date, and function pages.

This chunk is especially responsible for the user-visible report layout:

- Top-level option behavior for differential coverage, owner/date bins, source annotations, source view suppression, frames, dark mode, table sorting, gzip output, function aliases, and HTML validation.
- Per-file processing that combines current trace data, optional baseline data, diff metadata, source annotation data, and coverage category maps into `SourceFile` and `SummaryInfo` structures.
- HTML table writers for directory/file rows, per-testcase detail rows, source-line rows, header summaries, owner summaries, date summaries, and function summaries.
- Static report assets such as `gcov.css`, color bar PNGs, sort icons, `.htaccess`, `cmd_line`, `profile.html`, and optional serialized coverage data.

## Main Control Flow

### Option normalization and top-level execution

Lines 7225-7638 are still executable top-level script code. After registering options in `%genhtml_options`, the script calls `lcovutil::parseOptions()` and exits on option parsing failure. The subsequent normalization step resolves global flags before any trace parsing:

- `--suppress-aliases` and the function-alias filter force `$merge_function_aliases`.
- `--serialize` enables `$buildSerializableDatabase`.
- `--no-html` implies `$no_sourceview`.
- Coverage threshold defaults cascade from generic `hi_limit`/`med_limit` to line, function, branch, and MC/DC thresholds.
- Rc-provided lists are copied into active lists for date bins, date labels, annotate scripts, select scripts, and function simplification scripts when the command line did not override them.
- External callbacks are configured through `lcovutil::configure_callback()` for source annotation, selection, and function-name simplification.
- `stop_on_error = 0` implicitly enables synthetic missing source files.
- `--flat` and `--hierarchical` are rejected together.
- Differential-navigation mode (`$show_tla`) is enabled for baseline or diff reports, while "legacy labels" are used for non-differential navigation.
- Annotation scripts imply date-bin reporting. Owner and date-bin options are rejected without annotation support.
- Supplying only one side of baseline/diff input produces a warning but still enables differential report mode.
- Dark mode rewrites TLA background/text color maps from the normal palette to the dark palette.

The script expands trace filename globs, computes default titles, resolves baseline files and dates, canonicalizes the CSS path, reads prolog/epilog templates, disables incompatible `--frames`/`--no-sourceview`, parses prefix options, constructs file/function sort lists, optionally loads `genpng`, creates the output directory, optionally saves copies of input trace/diff files, writes `cmd_line`, and finally calls `gen_html()` inside `eval`.

After `gen_html()` returns, the script records overall profile timing, reports unused include/exclude/source-directory patterns, evaluates coverage criteria, optionally serializes the top-level `SummaryInfo` tree with `Storable::store`, cleans callbacks, writes profile output, optionally validates HTML, converts accumulated ignorable errors into a nonzero exit code, and exits.

### `gen_html()`

`gen_html()` is the main report workflow:

1. Creates `ReadCurrentSource` and merges all current `.info` inputs through `AggregateTraces::merge()`.
2. Loads unified diff data, if provided, before baseline parsing so baseline source can be mapped through the diff.
3. Merges baseline trace inputs through `ReadBaselineSource` when present, or creates an empty `TraceFile` when a diff is provided without baseline data.
4. Checks path consistency across diff, baseline, and current trace data.
5. Determines filename prefixes automatically with `get_prefix()` unless `--no-prefix` or explicit prefixes were used.
6. Reads and filters optional testcase descriptions with `read_testfile()` and `remove_unused_descriptions()`.
7. Quotes callback-script arguments that contain spaces for display/debug consistency.
8. Writes CSS/PNG assets unless `--no-html`, and writes `.htaccess` for gzip output.
9. Instantiates `GenHtml->new($current_data)`, which drives the recursive directory/file processing defined earlier in the file but calls renderer functions in this chunk.
10. Verifies annotation scripts found at least one controlled file when annotation was requested.
11. Writes `descriptions.<ext>` when testcase descriptions exist.
12. Prints overall line/function/branch/MC/DC rates with `print_overall_rate()`.

The function returns the top-level `SummaryInfo` object from `GenHtml`.

### `process_file()`

`process_file($fileSummary, $parent_dir_summary, $trunc_dir, $rel_dir, $filename)` is the per-source-file bridge between trace data and page generation. It:

- Applies configured directory prefixes for display names.
- Pulls line, function, branch, and MC/DC trace structures from the current `TraceInfo` object.
- Populates the per-file `SummaryInfo` counts.
- Resolves baseline filename mappings through `$diff_data->baseline_file_name()` and fetches baseline data from `$base_data`.
- Constructs `FileCoverageInfo`, which categorizes line/function/branch/MC/DC data into differential TLA buckets.
- Builds a `SourceFile`, which also updates file summary counts, date bins, owner bins, and "new file as baseline" category conversions.
- Skips empty files.
- Temporarily attaches the parent directory summary to the file summary so HTML callbacks can build directory links.
- Writes the source view unless `--no-sourceview`.
- Builds function proportion maps for line, branch, and MC/DC coverage per function when `--show-proportion` is enabled.
- Writes one or more function pages when function coverage is enabled and the file has visible functions.
- Writes frame support files and overview PNGs when `--frames` is enabled.
- Returns per-testcase line/function/branch/MC/DC data to the caller so directory pages can show detail rows.

This function is the central integration point for `TraceFile`, `TraceInfo`, `FileCoverageInfo`, `SourceFile`, and the HTML writers.

### Directory, file, and summary pages

`write_summary_pages()` removes empty children from a `SummaryInfo`, drops empty directories from the output tree, emits optional console TLA summaries, decides whether owner/date bin pages are needed, and builds a list of directory page calls for every requested sort and detail permutation. It creates:

- Default `index.<ext>` pages.
- Sort variants for line/function/branch/MC/DC coverage.
- Detail variants when `--show-details` and per-testcase data are available.
- Date and owner bin summary pages when annotation/owner options are enabled.

`write_dir_page()` creates the concrete HTML page, writes a standard header, emits the file table when sources exist, or writes an empty-coverpoints message when a selected subset has no coverpoints.

`write_file_table()` writes the full directory/file table. It supports three primary keys:

- `name`: standard file or directory rows.
- `owner`: rows grouped by owner, with files/directories shown beneath each owner.
- `date`: rows grouped by age bin, with files/directories shown beneath each bin.

It also supports two secondary detail modes when primary key is `name`:

- `-owner`: expand owner rows underneath each file/directory.
- `-date`: expand age-bin rows underneath each file/directory.

The table writer dynamically includes line, MC/DC, branch, and function columns depending on enabled coverage types and actual data. It suppresses function columns for owner grouping because function ownership is not associated. It can show per-testcase detail rows by computing affecting tests with `get_affecting_tests()`.

## Important APIs and Functions

### User-facing and setup helpers

- `print_usage(*HANDLE)`: emits the CLI usage text for common, operation, and HTML-output options.
- `print_overall_rate($trace, $ln_do, $fn_do, $br_do, $mcdc_do, $summary)`: prints source-file count and aggregate rates. In TLA mode, it also prints nonzero TLA counts by coverage type.
- `compute_title($patterns, $info_files)`: chooses a title from a single file, a single glob/pattern, or the number of expanded coverage DB files.
- `parse_dir_prefix(@prefixes)`: splits command-line prefix entries by `lcovutil::split_char` and appends them to `@dir_prefix`.
- `apply_prefix($filename, @prefixes)`: removes the first matching configured prefix from a path, returning `root` when the whole filename equals the prefix.
- `get_prefix($min_dir, @filename_list)` and `shorten_prefix($path)`: choose a prefix that minimizes displayed path lengths while preserving at least the requested number of parent directories.
- `get_relative_base_path($subdirectory)`: computes `../` path segments for CSS/image links from nested output directories.

### Input and text processing

- `read_testfile($desc_filename)`: parses testcase description files with `TN:` and `TD:` records, sanitizes testcase names to word characters, and reports format/empty-file errors through `lcovutil::ignorable_error()`.
- `remove_unused_descriptions()`: removes descriptions whose test names are not present in `%current_data`.
- `escape_html($string)`: escapes `&`, `<`, `>`, and `"`, optionally expands tabs into spaces, and converts newlines to `<br>`.
- `escape_id($name)`: normalizes HTML anchor IDs to HTML 4.01-compatible characters.
- `get_date_string($time)`: formats timestamps as `yyyy-mm-dd hh:mm:ss`, using `SOURCE_DATE_EPOCH` when no explicit time is provided.
- `simplify_function_name($name)`: invokes the configured simplification callback and reports callback failures as ignorable callback errors.

### File creation and static assets

- `html_create(*HANDLE, $filename)`: opens an output HTML file under `$output_directory`, lowercasing the full path on case-insensitive platforms. With `--html-gzip`, it opens a pipe to `gzip -c > $filename`.
- `write_png_files()`: writes embedded PNG byte arrays for coverage bar colors (`ruby.png`, `amber.png`, `emerald.png`, `snow.png`), `glass.png`, and `updown.png` when table sorting is active.
- `write_htaccess_file()`: writes `.htaccess` with gzip HTML encoding.
- `write_css_file()`: either copies a user CSS file or writes generated `gcov.css`. The generated CSS defines page layout, header tables, file tables, owner/date rows, source lines, function rows, legends, TLA classes, and dark-mode/normal palette substitutions.
- `get_html_prolog($file)` and `get_html_epilog($file)`: read user templates or provide default HTML 4.01 Transitional wrappers with `@pagetitle@` and `@basedir@` substitutions.

### Generic HTML layout

- `write_html(*HANDLE, $html_code)`: strips one leading tab from every line and writes to the HTML handle.
- `write_html_prolog(*HANDLE, $base_dir, $pagetitle)`: substitutes title and base path in the configured prolog.
- `write_header_prolog()`, `write_header_line()`, and `write_header_epilog()`: build the shared title/header table.
- `write_html_epilog(*HANDLE, $base_dir, $break_frames?)`: writes footer/version text and the configured epilog. It adds `target="_parent"` when the page can be embedded in frames.
- `write_frameset()`, `write_overview()`, and `write_overview_line()`: create frameset and overview image-map pages for source views.

### Header and summary table builders

- `write_header(*HANDLE, $callback_type, $ctrl, $trunc_name, $rel_filename, $summary, $fileDetail, $differentialFunctionMap)`: builds the standard page header for directory, file, source, testcase-description, and function pages. It constructs breadcrumb/navigation links, test/baseline labels and dates, optional command/profile links, legends, active TLA column lists, line/function/branch/MC/DC summary rows, date-bin summaries, and owner summaries. It returns a map from coverage type to the active nonzero TLA columns used by file tables.
- `build_html_path($path, $key, $bin_type, $isFile, $isAbsolute)`: builds clickable hierarchical breadcrumbs.
- `buildHeaderSummaryTableRow()`: creates TLA count cells for a coverage type, linking nonzero counts to first source locations when a `SourceFile` is available.
- `buildDateSummaryTable()`: creates date-bin rows for line/function/branch/MC/DC coverage, including links to detail pages or source anchors.
- `buildOwnerSummaryTable()`: creates owner-bin rows, optionally filtering owners without uncovered code unless `--show-owners all` is active.
- `max($a, $b)`: small row-count helper.

### File and testcase tables

- `write_file_table_prolog()`: writes multi-row table headers, including optional owner/date bin columns and sortable subcolumn headings.
- `write_file_table_entry()`: writes a primary or secondary row for a file, directory, owner, or date bin. It builds links to source pages, directory pages, bin summary anchors, and first TLA locations; computes bar graphs and rate classes; writes found/hit/missed and TLA counts; and adds footnote markers for elided rows.
- `write_file_table_detail_entry()`: writes per-testcase detail rows beneath a file/directory row.
- `write_file_table_epilog()`: closes the file table.
- `get_sort_code()`, `get_file_code()`, `get_line_code()`, `get_func_code()`, `get_br_code()`, and `get_mcdc_code()`: build sortable column heading labels and links.
- `get_bar_graph_code($base_dir, $found, $hit)`: renders a 100-pixel coverage bar with color chosen by line-coverage thresholds.
- `classify_rate($found, $hit, $med, $hi)`: returns low/medium/high rate bucket indexes.
- `get_affecting_tests()`: returns testcase-level line/function/branch/MC/DC totals only for tests with nonzero line hits.

### Source-line rendering

- `write_source($srcfile, $count_data, $checkdata, $fileCovInfo, $funcdata, $sumbrcount, $mcdc_summary)`: writes a source view for one file and returns compact per-line data for `gen_png()`. It suppresses branch/MC/DC columns when no data exists, creates a `PrintCallback`, applies optional `--select-script` region elision, validates source checksums, and delegates each visible line to `write_source_line()`.
- `write_source_prolog()` and `write_source_epilog()`: open and close the source view table and fixed-width source `<pre>`.
- `write_source_line()`: renders one source line with optional age, owner, line number, branch symbols, MC/DC symbols, TLA label, hit count, source text, annotation tooltip, deleted-line marker, and next-navigation anchors. It also emits continuation rows when branch/MC/DC text exceeds the fixed field width.
- `format_count($count, $width)`: right-aligns counts and switches to a compact `>N*10^E` notation for values that do not fit.
- `fmt_centered($width, $text)`: centers source heading labels.

### Branch and MC/DC rendering

- `get_block_list($branch_or_mcdc_data)`: groups branch locations or MC/DC expressions into display blocks. Branch data becomes `[block, branch, record, length, open, close]`; MC/DC data is expanded into true and false senses per expression.
- `get_block_len($block)`: sums display widths for a branch/MC/DC block.
- `distribute_blocks($blocks, $field_width)`: wraps blocks over one or more fixed-width lines while trying to keep groups together.
- `get_branch_html($brdata, $cbdata)`: converts branch records into colored symbols: `+` for taken, `-` for not taken, `#` for not executed, and `x` for excluded. In differential mode it uses TLA classes and links to the next branch group with the same TLA.
- `get_mcdc_html($mcdc_data, $cbdata)`: converts MC/DC expressions into colored true/false sensitization symbols: `T`/`F` for sensitized, `t`/`f` for not sensitized, `-` for dropped, and `x` for excluded. Differential mode mirrors branch TLA navigation.

### Function pages

- `write_function_page()`: chooses output filenames for function tables by sort mode, writes the shared header, and calls `write_function_table()`.
- `funcview_get_label()`: returns function table headings with sort links for function name, hit count, unexercised lines, unexercised branches, or unexercised MC/DC expressions.
- `funcview_get_sorted()`: sorts function names alphabetically, by hit count, or by descending missed line/branch/MC/DC counts.
- `write_function_table()`: writes rows for function leader entries and optional alias rows. It hides deleted functions (`DUB`, `DCB`), applies function-name simplification, links functions back to source anchors, displays differential TLA labels, and optionally shows per-function line/branch/MC/DC rates.

## State and Persistence Behavior

This chunk relies on global mutable script state rather than passing an explicit context object. Important globals include:

- Input and title state: `@info_filenames`, `@base_filenames`, `$diff_filename`, `$test_title`, `$baseline_title`, `$current_date`, `$baseline_date`, `$age_basefile`.
- Output behavior: `$output_directory`, `$html_ext`, `$html_gzip`, `$html_prolog`, `$html_epilog`, `$css_filename`, `$no_html`, `$no_sourceview`, `$frames`, `$flat`, `$hierarchical`, `$sort_tables`, `$validateHTML`.
- Coverage thresholds and labels: `$ln_med_limit`, `$ln_hi_limit`, `$fn_med_limit`, `$fn_hi_limit`, `$br_med_limit`, `$br_hi_limit`, `$mcdc_med_limit`, `$mcdc_hi_limit`, `@rate_name`, `@rate_png`, `$show_tla`, `$use_legacyLabels`, `$show_hitTotalCol`, `$opt_missed`.
- Differential and annotation state: `$diff_data`, `$base_data`, `$current_data`, `@SourceFile::annotateScript`, `$show_dateBins`, `$show_ownerBins`, `$show_nonCodeOwners`, `$show_zeroTlaColumns`, `@datebins`, `@SummaryInfo::ageGroupHeader`.
- Path/rendering state: `@dir_prefix`, `@opt_dir_prefix`, `@fileview_prefixes`, `@fileview_sortlist`, `@funcview_sortlist`, `$tab_size`, `$charset`, `$footer`, `$legend`.
- Description and profile state: `%test_description`, `$lcovutil::profileData`, `$lcovutil::profile`.

Persistent side effects are all report artifacts under `$output_directory`:

- `cmd_line` is always written before `gen_html()`.
- `gcov.css`, color/sort PNGs, and optional `.htaccess` are written unless HTML is suppressed where applicable.
- `index*.html` and nested directory `index*.html` pages are generated for default, detail, sorted, owner, and date views.
- Per-file source pages use `<basename>.gcov.<ext>`.
- Per-file function pages use `<basename>.func.<ext>`, `<basename>.func-c.<ext>`, `<basename>.func-l.<ext>`, `<basename>.func-b.<ext>`, and `<basename>.func-m.<ext>` depending on sort/data availability.
- Frame mode adds `<basename>.gcov.png`, `<basename>.gcov.frameset.<ext>`, and `<basename>.gcov.overview.<ext>`.
- Test descriptions are written to `descriptions.<ext>`.
- `profile.html` and profile data are saved through `lcovutil::save_profile()`.
- Optional `--serialize` writes a `Storable` dump to the configured serialization path.
- Optional `--save` copies baseline, diff, and current trace inputs into the output directory.

## Dependencies and Integration Points

The chunk integrates with many packages defined elsewhere in `genhtml` and lcov support modules:

- `lcovutil`: option parsing, rc/profile state, logging, ignorable warnings/errors, palette maps, rate formatting helpers, coverage filters, path separators, callback configuration/cleanup, HTML validation trigger support, and profile saving.
- `AggregateTraces`: glob expansion and merging of trace files.
- `TraceFile`/`TraceInfo`: current and baseline coverage records.
- `ReadCurrentSource` and `ReadBaselineSource`: source lookup and checksum/source loading behavior.
- `FileCoverageInfo`: differential classification maps for lines, branches, MC/DC, and functions.
- `SourceFile`: annotated source lines, owner/date metadata, navigation lookups, and source-detail state.
- `SummaryInfo`: hierarchical coverage totals, TLA count accessors, owner/date aggregation, active age bins, sorting, and parent/child summary relationships.
- `FileOrDirectoryCallback`, `FileOrDirectoryOwnerCallback`, and `FileOrDirectoryDateCallback`: table row adapters that supply totals, callbacks, secondary rows, and file/directory links.
- `PrintCallback`: stateful helper for source-line rendering and next-link suppression.
- `CoverageCriteria`: optional post-generation criteria checks.
- `ValidateHTML`: optional output validation.
- `Date::Parse`, `DateTime`, `Time::HiRes`, `Storable`, `File::Spec`, `File::Basename`, `File::Path`, `File::Copy`, `Digest::MD5`, and external `gzip`/`cp` commands.
- `genpng`: loaded dynamically for frame overview PNG generation.

Callback integration is significant. Annotation, selection, version, resolve, criteria, and function-simplification scripts can alter which source lines are loaded, which regions are visible, how owners/dates are shown, how criteria affect exit status, and how function names appear.

## Risks and Edge Cases

- `html_create()` uses a shell pipeline string for gzip output: `gzip -c > $filename`. Filenames are derived from output paths, but shell interpretation still makes quoting and metacharacter safety important.
- `write_css_file()` shells out to `cp` for user CSS copying. It passes arguments as a list, which avoids shell interpolation, but failures only report `$!`, which may not describe nonzero exit status accurately.
- HTML is mostly hand-assembled. `escape_html()` is applied in many user/source-facing paths, but not uniformly for every constructed string. Callback output, custom prolog/epilog/footer, `--rc desc_html`, and some labels are intentionally trusted, so XSS/content-injection behavior depends on trusted input.
- A typo calls `lcovutil::ignorable_eror()` in the owner/date source-line path for undefined owner/age metadata. If that path is reached, it may fail with an undefined subroutine instead of reporting an ignorable error.
- The generated CSS includes `foreground-color` for `span.lineNumWithDelete`, which is not a valid CSS property; expected behavior likely meant `color`.
- Global state makes option interactions fragile. For example, `--no-html` changes source-view behavior, `--frames` is disabled by `--no-sourceview`, owner/date tables require annotation scripts, and TLA output mode changes hit-total columns and labels.
- `get_prefix()` is heuristic and uses resolved/absolute paths, so unusual path mappings, symlinks, or mixed absolute/relative trace paths can produce surprising display prefixes.
- Source selection elision in `write_source()` resets callback state across gaps and emits synthetic elision lines. Navigation correctness depends on `InInterestingRegion`, `PrintCallback`, and `SourceFile` next-location methods staying in sync.
- The branch and MC/DC formatting code relies on fixed field widths and handwritten display lengths. HTML tags are later stripped for continuation alignment, which is brittle when markup changes.
- Date/owner navigation assumes owner and age metadata exist for project code lines when annotation is enabled. Missing metadata can affect source rendering and table anchors.
- Function pages suppress deleted functions and optionally aliases. Merging/suppressing aliases changes table contents and sort results, which can confuse comparisons unless documented to users.
- `write_file_table()` has many combinations of primary key, bin type, detail view, flat/hierarchical mode, and source-view suppression. Link generation is the highest-risk area for regressions.
- MC/DC summary styling in `write_header()` uses branch thresholds (`$br_med_limit`, `$br_hi_limit`) for one header row path rather than MC/DC-specific thresholds, which may be intentional legacy behavior or a threshold bug.

## Test Signals

Useful validation signals for this chunk include:

- Run `genhtml` on a simple line-only trace and verify `index.<ext>`, `gcov.css`, PNG assets, `cmd_line`, and per-file source pages are created.
- Run with `--function-coverage`, `--branch-coverage`, and `--mcdc-coverage` traces to verify dynamic columns, source-line branch/MC/DC glyphs, and function pages.
- Run with `--baseline-file` and `--diff-file` to exercise TLA categories, differential colors, first/next navigation links, deleted-line markers, and hidden deleted functions.
- Run with `--annotate-script`, `--show-owners`, and `--date-bins` to verify owner/date header tables, source owner/date columns, owner/date detail pages, truncation behavior, and non-project file handling.
- Run `--show-details` with testcase descriptions to verify `descriptions.<ext>`, per-testcase detail rows, and description anchors.
- Run `--flat`, `--hierarchical`, and default layout separately to validate relative links and breadcrumbs.
- Run `--no-sourceview`, `--no-html`, and `--frames` combinations to ensure incompatible options are disabled or skipped as expected.
- Run `--html-gzip` and verify compressed HTML output plus `.htaccess`.
- Run `--dark-mode`, `--simplified-colors`, and default palettes to verify generated CSS classes and PNG bar assets.
- Run `--sort`/`--no-sort` and inspect generated sort pages and `updown.png` references.
- Run with `--serialize` and a coverage criteria script to confirm serialized top-level data and final exit status behavior.

## Chunk Boundary Notes

The chunk invokes several classes and methods whose definitions are outside this line range, notably `GenHtml->new`, `SummaryInfo` aggregation methods, `SourceFile` navigation methods, `FileCoverageInfo` categorization, and callback adapter classes. This research therefore describes their integration contracts as observed from calls in lines 7225-14230, not their internal implementations.
