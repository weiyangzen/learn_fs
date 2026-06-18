# sources/test-tools/strace/maint/gen/xmalloc.c

Purpose: fail-fast allocation helpers for the standalone generator.

Important APIs/types/functions: `die_out_of_memory`, `free_by_pointer`, `xmalloc`, `xcalloc`, `xstrdup`, and `xasprintf`.

Control flow: each allocation wrapper calls the libc allocator, exits with an error message on failure, and returns allocated memory otherwise. `xasprintf` wraps `vasprintf`.

State and persistence behavior: no persistent state except heap allocations returned to callers. `free_by_pointer` supports GCC cleanup attributes by freeing and nulling a pointer variable.

Dependencies and integration points: included across maint/gen to avoid repetitive allocation checks and support `CLEANUP_FREE`.

Risks: exits on allocation failure rather than propagating errors. `xasprintf` calls `va_end` only after successful `vasprintf`; if `vasprintf` fails and exits, cleanup is skipped but process termination makes it immaterial.

Test signals: normal generator build/run validates use sites; fault-injected allocation tests would confirm fail-fast behavior.
