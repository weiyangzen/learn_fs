# sources/test-tools/strace/src/xmalloc.c

Purpose: `xmalloc.c` implements strace's fail-fast allocation helpers. They wrap libc allocation, duplication, and formatted-allocation APIs so callers do not need to propagate out-of-memory errors through every decoder path.

Important APIs/types/functions: public functions are `xmalloc`, `xcalloc`, `xallocarray`, `xreallocarray`, `xgrowarray`, `xstrdup`, `xstrndup`, `xmemdup`, `xarraydup`, and `xasprintf`. The internal `die_out_of_memory` uses `error_msg_and_die("Out of memory")` and a recursion guard; the file depends on `<stdlib.h>`, `<string.h>`, `<stdarg.h>`, `<stdio.h>`, `error_prints.h`, `macros.h`, and `xmalloc.h`.

Control flow: each wrapper calls the corresponding libc routine, checks the result, and terminates on failure. `xallocarray` and `xreallocarray` compute `nmemb * size` and validate multiplication overflow before allocation. `xgrowarray` computes a growth increment from either a default allocation target or half the existing element count, checks count overflow, updates the caller's element count, and reallocates through `xreallocarray`. `xstrndup` uses system `strndup` when available and otherwise allocates/copies manually. `xasprintf` wraps `vasprintf` around a `va_list`.

State/persistence behavior: the only internal state is the static `recursed` flag in `die_out_of_memory`, preventing recursive diagnostic allocation failures from looping. Allocation state is returned to callers as heap memory; no persistent files or global registries are maintained.

Dependencies and integration points: these helpers are included throughout strace binaries wherever decoder support code needs memory with fatal-on-failure semantics. `xmalloc.h` renames `xmalloc`/`xcalloc` to `strace_malloc`/`strace_calloc` at preprocessing time, so this implementation is part of a package-wide allocation namespace contract.

Risks: zero-size allocation behavior follows libc and still treats a `NULL` return as fatal; code relying on non-fatal `realloc(ptr, 0)` semantics should not use these wrappers. Overflow checks are critical for array helpers. The manual `strndup` fallback copies exactly `n` bytes and appends a terminator, so callers must pass a valid source with at least the intended readable range.

Test signals: unit or integration coverage should exercise overflow rejection in `xallocarray`/`xreallocarray`, growth from `NULL` and non-`NULL` arrays, NULL-preserving duplication helpers, `xasprintf` formatting, and fatal-path behavior through controlled allocation failure or wrappers.
