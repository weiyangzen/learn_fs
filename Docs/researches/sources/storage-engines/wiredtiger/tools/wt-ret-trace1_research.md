# sources/storage-engines/wiredtiger/tools/wt-ret-trace1

Purpose: destructive Perl source-rewriting tool that assigns unique negative error codes to individual WiredTiger error-return sites so identical base errors can be traced back to the exact file/function/line where they originated.

Important APIs and control flow: help text describes the workflow and warns about in-place modification. The script confirms when run interactively unless `-y`, `-q`, or `-f` is used, changes to the git top level, scans `src/**/*.c/h`, parses return/error macro calls with recursive regex token patterns, replaces base error constants with generated `ERR_AT_func___file_line` symbols, records mappings, rewrites comparisons/cases in `src`, `bench`, `test`, `ext`, and `examples` to use generated `WT_E_EQ__ERR()` helpers, rewrites `src/include/error.h` comparisons, prepends `#pragma once` and appends generated defines/macros to `src/include/wiredtiger.h.in`, then relaxes CMake `-Werror` to `-Wno-gnu-statement-expression`. Optional thread support parallelizes first-pass source processing with `pmap()`.

State and persistence behavior: heavily mutates source files in place across the repository. It writes generated macro definitions into `wiredtiger.h.in` and changes CMake files. It prints the base-error regex at the end.

Dependencies and integration points: depends on Perl 5.27, optional Perl threads, git, find, shell commands, and WiredTiger source layout. It targets WT error macros such as `WT_RET`, `WT_ERR`, `WT_TRET`, `WT_RET_MSG`, `WT_ERR_PANIC`, and comparison sites.

Risks: extremely high blast radius and intentionally destructive. Regex parsing of C is sophisticated but still heuristic; macros, generated files, comments, or unusual formatting can be rewritten incorrectly. Generated error-code ranges leak through public API unless `WT_E_BASE()` is applied at API boundaries. It modifies build flags globally. It should only be used on a disposable branch/worktree.

Test signals: after running, CMake/build failures identify missed rewrites; runtime with verbose `error_returns` can trace unique codes. The help text includes a follow-up workflow for wrapping generated codes in `__wt_set_return()`.
