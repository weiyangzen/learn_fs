# sources/test-tools/lcov/bin/llvm2lcov

## Purpose

`llvm2lcov` converts JSON coverage exported by `llvm-cov export -format=text` into LCOV `.info` format. It supports line coverage, function coverage, branch coverage, and LLVM MC/DC records when requested and available. It is intended for Clang/LLVM instrumentation workflows using `llvm-profdata` and `llvm-cov`, then feeding LCOV/genhtml reporting.

## Important APIs, types, and functions

- `print_usage()` documents the LLVM workflow and tool-specific options.
- `parse($testname, @json_files)` is the core converter. It loads one or more JSON files, validates the top-level `data` array, resolves source paths, skips excluded files, creates `TraceFile`/per-file entries, and fills line/function/branch/MC/DC maps.
- `JsonSupport::load()` from `lcovutil` reads JSON. `version->parse()` handles LLVM JSON version comparisons.
- `ReadCurrentSource` resolves paths and extracts source expressions for branch and MC/DC labels.
- `TraceFile`, per-file `data()`, `test()`, `testfnc()`, `testbr()`, and `testcase_mcdc()` store output coverage.
- `BranchData`, `BranchBlock`, and `BranchElement` represent branch alternatives derived from LLVM branch regions.
- `MCDC_Data` records MC/DC blocks and expressions. The script has separate paths for JSON versions before `3.0.1` and for `3.0.1` or newer because LLVM changed MC/DC record shape and file-id handling.
- Command-line parsing uses `lcovutil::parseOptions()` with `--test-name` and `--output-filename`, plus common LCOV options handled by the shared parser.

## Control flow

The command-line path parses options, defaults output to `llvm2lcov.info`, calls `parse()`, applies filters, writes the LCOV info file, prints a summary, checks coverage criteria, summarizes messages, cleans callbacks, and exits according to criteria status.

Inside `parse()`, each JSON file is loaded and each `data` entry is traversed. File records are processed first: source paths are resolved, excluded files are skipped, file versions may be attached, and LLVM segment arrays are converted into LCOV line counts by walking adjacent segment boundaries. For older MC/DC JSON, file-level `mcdc_records` are combined with `MCDCBranchRegion` branch entries and source expressions.

Function records are then processed. The converter defines functions at their first region start line, adds execution counts, optionally builds branch blocks from LLVM branch arrays, and optionally builds MC/DC expression blocks. For newer JSON versions, it handles file IDs and expansion IDs so macro/expanded regions can be attributed to useful source locations. After all files are parsed, summary maps are built by unioning testcase-specific line, branch, function, and MC/DC data into each file's aggregate maps.

## State and persistence behavior

The persistent output is a single LCOV `.info` file. The converter keeps all parsed coverage in one `TraceFile` object until writing. It reads current source files for expression extraction but does not modify them. Global LCOV filter, exclusion, coverage-mode, verbosity, criteria, and callback state comes from `lcovutil`.

## Dependencies and integration points

The script depends on Perl `version`, common file/path modules, `Capture::Tiny`, `Storable`, `POSIX`, and the shared `lcovutil` library. It integrates with LLVM JSON schema fields including `data`, `files`, `functions`, `segments`, `branches`, `regions`, `expansions`, `summary`, and `mcdc_records`. Its output is standard LCOV trace data for `lcov`, `genhtml`, and related tools.

## Risks and edge cases

- The converter assumes exact array sizes for segments, branches, and MC/DC records. Unsupported LLVM schema changes cause dies or ignorable format errors.
- Line-count derivation from segments is subtle: adjacent same-line segments, region entries, gaps, and max-count selection can affect reported counts.
- MC/DC handling differs across JSON versions and expansion/file-id combinations. Missing source files or expression extraction failures degrade expression labels to numeric indexes.
- Branch block IDs are synthetic because LLVM JSON does not provide the same block identity as gcov; multiple expressions on one line are grouped by line with generated element indexes.
- Exclusion is source-path dependent, so path resolution and substitutions must match the JSON filenames and local filesystem.
- The script imports many modules also used by `geninfo`; some are not directly used in the current converter path, increasing maintenance noise.

## Test signals

Tests should convert minimal LLVM JSON for line-only coverage, functions, branches, macro expansions, excluded files, multiple JSON inputs, and MC/DC for both pre-`3.0.1` and `3.0.1+` schema variants. Output should be validated with `lcov --list` and `genhtml`. Negative tests should cover missing files, malformed JSON, unexpected array sizes, unsupported MC/DC entry sizes, skipped source filters, and coverage criteria failures.
