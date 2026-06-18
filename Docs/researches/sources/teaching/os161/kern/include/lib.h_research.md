# File Research: sources/teaching/os161/kern/include/lib.h

Declares common kernel library functions and macros.

Key contents:
- Assertions: `KASSERT`, `DEBUGASSERT`, `badassert`.
- Debug flags including `DB_SEMFS` and `DB_SFS`; `DEBUG` prints conditionally on `dbflags`.
- Kernel heap APIs: `kmalloc`, `kfree`, heap stats/leak helpers.
- String/memory APIs, `snprintf`, `strerror`.
- Console APIs: `putch`, `getch`, `kprintf`, `panic`, `kgets`.
- Utility macros `DIVROUNDUP` and `ROUNDUP`.

Relevance:
- SFS and semfs use allocation, string/memory helpers, assertions, debug printing, panic, and rounding.
