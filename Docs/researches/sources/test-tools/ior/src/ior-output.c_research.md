# sources/test-tools/ior/src/ior-output.c

## Purpose
Handles user-visible IOR output in default text, CSV, and JSON-like formats. It prints run headers, test setup, per-iteration reduced metrics, removal timing, short summaries, and long all-test summaries.

## Important APIs, Types, And Functions
Public functions include `PrintTableHeader`, `PrintKeyVal`, `PrintRepeatEnd`, `PrintRepeatStart`, `PrintTestEnds`, `PrintReducedResult`, `PrintHeader`, `ShowTestStart`, `ShowTestEnd`, `ShowSetup`, `PrintLongSummaryOneTest`, `PrintLongSummaryHeader`, `PrintLongSummaryAllTests`, `PrintShortSummary`, and `PrintRemoveTiming`. Internal helpers include `PrintNextToken`, section/array printers, `PrintKeyValDouble`, `PrintKeyValInt`, `bw_ops_values`, `bw_values`, `ops_values`, `PrintLongSummaryOneOperation`, `PPDouble`, and `mean_of_array_of_doubles`.

## Control Flow
Rank 0 prints the run header, begins a tests array/section, and for each test prints start metadata, filesystem size, options, and a results array. `ior.c` calls `PrintReducedResult` after MPI-reduced timings are available. Summaries compute per-repetition bandwidth and operations statistics from `IOR_results_t`. JSON output is managed by global indentation and comma-token state; CSV output emits flat rows; default output emits human-readable tables.

## State And Persistence Behavior
The file keeps static `indent` and `needNextToken` formatting state. It writes to global `out_resultfile` and sometimes `out_logfile`. It does not persist files itself except through caller-provided output streams; stonewalling status storage is triggered from `ShowTestEnd` through utility functions.

## Dependencies And Integration Points
Depends on `ior.h`, `ior-internal.h`, `utilities.h`, global `rank`, `verbose`, `outputFormat`, `out_resultfile`, `out_logfile`, and environment variables for verbose dumps. Calls `GetTestFileName`, `ShowFileSystemSize`, `HumanReadable`, `CurrentTimeString`, and stonewalling utilities.

## Risks And Edge Cases
JSON generation is manual and does not escape strings, so command lines, file names, or environment-derived values containing quotes/backslashes can produce invalid JSON. `PrintKeyVal` mutates the passed value when it ends in newline. Several functions early-return for nonzero ranks, which must match caller synchronization. `PrintArrayEnd` decrements `indent` even though `PrintArrayStart` does not increment it, making indentation state fragile. Summary calculations divide by timings and transfer sizes and can emit infinities for zero elapsed time.

## Test Signals
Golden output tests for default, CSV, and JSON formats; command lines with special characters; multi-repetition summaries; stonewalling summary paths; and rank-gated output under MPI validate this code.
