# sources/test-tools/strace/maint/gen/xmalloc.h

Purpose: declarations and GCC attribute macros for the generator allocation helpers.

Important APIs/types/functions: `ATTRIBUTE_FORMAT`, `ATTRIBUTE_MALLOC`, `ATTRIBUTE_ALLOC_SIZE`, `ATTRIBUTE_CLEANUP`, `CLEANUP_FREE`, and prototypes for allocation/string helpers.

Control flow: not executable; annotations improve compiler diagnostics and cleanup ergonomics.

State and persistence behavior: no state.

Dependencies and integration points: used by all handwritten generator modules and by `deflang.h`.

Risks: depends on GNU C attributes, matching `CPPFLAGS=-std=gnu99`. Porting to non-GNU compilers would require compatibility shims.

Test signals: compiler format warnings for `xasprintf` callers and successful `CLEANUP_FREE` usage in codegen validate the declarations.
