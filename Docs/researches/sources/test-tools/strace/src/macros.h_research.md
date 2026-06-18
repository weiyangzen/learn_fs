<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/macros.h -->
# sources/test-tools/strace/src/macros.h

Purpose: shared compile-time and utility macros used throughout strace.
Important APIs/types/functions: `ARRAY_SIZE`, `ARRSZ_PAIR`, `STRINGIFY`, `MIN/MAX/CLAMP`, `ROUNDUP`, `containerof`, type-comparison helpers, alignment helpers, and conditional feature macros.
Control flow: preprocessor and compile-time expressions only. State and persistence behavior: no runtime state.
Dependencies and integration points: included by many headers, including `list.h` and mpers headers. Risks: macro double-evaluation and compiler-extension assumptions must stay controlled. Test signals: full build matrix, static assertions, and code paths that exercise array/type macros.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/macros.h -->
