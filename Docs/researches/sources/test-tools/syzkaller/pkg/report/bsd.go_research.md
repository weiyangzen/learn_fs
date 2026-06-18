# sources/test-tools/syzkaller/pkg/report/bsd.go

Purpose: Shared BSD-style report implementation for crash detection, parsing, and symbolization used by Darwin/OpenBSD-like reporters.

Important APIs and types: `bsd` stores config, oops definitions, regexes for symbolizable lines, kernel object path, and text symbols. `ctorBSD` constructs the reporter implementation. Methods `ContainsCrash`, `Parse`, `Symbolize`, and `symbolizeLine` implement reporter behavior.

Control flow: `ctorBSD` reads text symbols from `<kernel_obj>/<target.KernelObject>` when a kernel object directory is configured. `ContainsCrash` delegates to common `containsCrash`; `Parse` delegates to `simpleLineParser`. `Symbolize` iterates report lines, calls `symbolizeLine`, and adjusts `reportPrefixLen` if symbolization changes bytes before the prefix boundary. `symbolizeLine` matches configured regexes, extracts function and hex offset, finds the function in text symbols, constructs a kernel PC, calls symbolizer, and inserts file:line and inline function annotations.

State and persistence: Symbol table is cached in the reporter instance. No filesystem writes.

Dependencies and integration: Uses common report parsing helpers, `symbolizer`, and `mgrconfig.KernelDirs`. Darwin uses this via `ctorDarwin`.

Risks: Assumes a 32-bit-style high-half address calculation when building `fnStart`. Symbolization depends on regex capture group layout. Missing symbols or symbolizer errors silently leave lines unchanged.

Test signals: `bsd_test.go` supplies synthetic symbols and frames to validate line symbolization and inline frame expansion.
