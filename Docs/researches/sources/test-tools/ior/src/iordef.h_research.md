# sources/test-tools/ior/src/iordef.h

## Purpose
Provides common IOR definitions, portability shims, constants, enums, and scalar typedefs shared by core code and backends.

## Important APIs, Types, And Functions
Defines `ior_dataPacketType_e`, `ior_memory_flags`, `enum OutputFormat_t`, boolean constants, decimal and binary byte constants, access-mode constants `WRITE`/`WRITECHECK`/`READ`/`READCHECK`, verbosity levels, `MAX_STR`, `MAX_HINTS`, `MAX_RETRY`, `PATH_MAX`, parser delimiters, `FILENAME_DELIMITER`, `IOR_offset_t`, `IOR_size_t`, and `IOR_format`. Adds Windows compatibility definitions for POSIX-like functions and `utsname`.

## Control Flow
No runtime control flow is implemented here. The constants and enums steer parsing, validation, data generation, transfer loops, and output formatting across the benchmark.

## State And Persistence Behavior
No state or persistence. It standardizes integer widths for offsets and transfer sizes as signed long long values.

## Dependencies And Integration Points
Optionally includes generated config, stdio/stdlib/string, Windows headers or POSIX headers. Included by `ior.h`, `aiori.h`, and backend code, making its definitions part of the common ABI.

## Risks And Edge Cases
`IOR_offset_t`/`IOR_size_t` are signed long long, so extremely large sizes can overflow in multiplications such as expected aggregate file size. Windows compatibility macros redefine common functions and can diverge from POSIX behavior. `random()` emulation only has noted limited entropy. Access mode constants are integers rather than an enum, so invalid values are possible.

## Test Signals
Cross-platform compilation, large-size parsing/validation tests, output format selection, access mode switch coverage, and Windows builds validate this file's assumptions.
