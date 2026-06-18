# sources/test-tools/strace/src/xmalloc.h

Purpose: `xmalloc.h` declares strace's fail-fast allocation API and documents the package-wide allocation contract: allocation failure terminates the process rather than returning errors to ordinary decoder code.

Important APIs/types/functions: declarations cover `xmalloc`, `xcalloc`, inline `xzalloc`, `xallocarray`, `xreallocarray`, `xgrowarray`, `xstrdup`, `xstrndup`, `xmemdup`, `xarraydup`, object helper macro `xobjdup`, and `xasprintf`. GCC compatibility annotations such as `ATTRIBUTE_MALLOC`, `ATTRIBUTE_ALLOC_SIZE`, and `ATTRIBUTE_FORMAT` give static analyzers and compilers allocation-size and printf-format knowledge. The header maps `xcalloc` to `strace_calloc` and `xmalloc` to `strace_malloc`.

Control flow: this header contributes mostly declarations, but `xzalloc` is an inline wrapper around `xcalloc(1, size)`, and `xobjdup(src_)` expands to `xmemdup(src_, sizeof(*(src_)))`. All other behavior is implemented in `xmalloc.c`.

State/persistence behavior: the header owns no mutable state. It defines source-level contracts that affect all translation units including it, especially the namespace aliases and NULL-preserving semantics of the string/memory duplication helpers.

Dependencies and integration points: depends on `<stddef.h>` and `gcc_compat.h`. It is integrated by many strace decoder and utility files that want fatal allocation semantics and by `xmalloc.c`, which provides the implementation.

Risks: the preprocessor aliases mean symbol names and declarations must remain synchronized with the implementation and build system. Misusing `xobjdup` with expressions that have side effects would be risky because it dereferences the expression in `sizeof` context for type sizing. Callers must remember that NULL input to duplication helpers returns NULL, while allocation failure never returns.

Test signals: compiler warnings from allocation/format attributes, successful package-wide linkage, and tests around allocation overflow/duplication behavior in `xmalloc.c` validate this header's contract.
