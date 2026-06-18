<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.sh -->
# sources/test-tools/lcov/tests/genhtml/exception/exception.sh

- Purpose: Genhtml exception-branch regression harness for throwing and nonthrowing builds, trace merging, exception branch filtering, and differential reports.
- Important APIs/types/functions: Defines shell functions `runClang` and `runGcc`; uses common tool variables, version scripts, compiler selection, and ignore/filter options.
- Control flow: Compiles `exception.cpp` with `DO_THROW` and `NO_THROW`, captures coverage, normalizes compiler quirks, merges traces in both directions, and renders genhtml normal/differential reports.
- State and persistence behavior: Creates executables, `.gcno/.gcda`, `.info`, logs, and report directories; clean removes them.
- Dependencies and integration points: Depends on gcc/clang/llvm-cov availability, lcov/genhtml/geninfo, `common.tst`, and source-control version callbacks.
- Risks: Compiler-specific exception branch layouts are the main risk; old gcc inconsistency is handled with filters/gates.
- Test signals: Passing signals are successful capture/merge/report commands and expected normalized branch/report comparisons.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.sh -->
