# sources/storage-engines/wiredtiger/src/os_common/os_getopt.c

## Purpose
Provides a public-domain getopt implementation namespaced as WiredTiger globals and optionally returning WiredTiger-specific error constants.

## Important APIs, Types, and Functions
The exported parser is `__wt_getopt`. Global parser state includes `__wt_opterr`, `__wt_optind`, `__wt_optopt`, `__wt_optreset`, `__wt_optwt`, and `__wt_optarg`.

## Control Flow
The parser maintains a static `place` pointer into the current argv element. It handles new option scanning, end-of-options `--`, solitary `-`, illegal options, options with required arguments, inline arguments, and next-argv arguments. When `__wt_optwt` is set, bad option/argument returns are `WT_GETOPT_BAD_OPTION` and `WT_GETOPT_BAD_ARGUMENT`; otherwise it returns traditional `?` or `:`.

## State and Persistence Behavior
All state is process-global and transient. Callers reset parsing through `__wt_optreset` and `__wt_optind`. There is no database persistence.

## Dependencies and Integration Points
Command-line tools and tests use this parser to avoid relying on platform getopt availability or behavior. It depends on stderr for optional diagnostics and WiredTiger return constants for WT-specific mode.

## Risks and Edge Cases
The API is not thread-safe because parser state is global and `place` is static. Callers must reset state between independent parses. `__wt_optwt` changes the error contract, so callers must know which mode is active.

## Test Signals
Tool argument parsing tests should cover grouped short options, missing arguments, inline and separated arguments, `--`, solitary `-`, parser reset, disabled error printing, and WT-specific error codes.
