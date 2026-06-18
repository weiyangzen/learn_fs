# sources/test-tools/ior/src/ior-internal.h

## Purpose
Declares private cross-file interfaces for IOR's internal implementation, primarily connecting `ior.c` with output/reporting functions in `ior-output.c` and exposing random offset generation to helper code.

## Important APIs, Types, And Functions
Declares `PrintHeader`, `ShowTestStart`, `ShowTestEnd`, `ShowSetup`, repeat and summary printers, `GetTestFileName`, `PrintRemoveTiming`, `PrintReducedResult`, `PrintTestEnds`, `PrintTableHeader`, and `GetOffsetArrayRandom`. Defines `struct results` for summary min/max/mean/variance/stddev/value arrays.

## Control Flow
`ior.c` calls these declarations while running tests: header before tests, setup and table header at test start, reduced result rows after each operation, repeat/test endings, short and long summaries, and removal timing. `ior-output.c` consumes `IOR_test_t`, `IOR_param_t`, and `IOR_results_t` from `ior.h`.

## State And Persistence Behavior
No state is stored in the header. It exposes output functions that write to global `out_resultfile`/`out_logfile` and helper state inside `ior-output.c`.

## Dependencies And Integration Points
Requires prior visibility of `IOR_param_t`, `IOR_test_t`, and `IOR_offset_t`, normally through including `ior.h` before this header. It is an internal boundary and not a public API for external users.

## Risks And Edge Cases
The header lacks includes/forward declarations for its parameter types, making include order significant. `struct results` includes a flexible-style trailing pointer allocated by callers, so allocation and ownership must remain coordinated with `ior-output.c`.

## Test Signals
Full IOR build, output-format tests, and compilation of translation units that include this header through the expected include order are the main signals.
