# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/compat.c

## Scope

Compatibility allocation and file-existence helpers for `5l`.

## Behavior

- Replaces `malloc()` with a hunk allocator backed by `gethunk()`.
- `free()` is a no-op; `calloc()` zeroes hunk allocations.
- `realloc()` aborts if used.
- `mysbrk()` wraps `sbrk()`.
- `fileexists()` checks existence through `stat()`.

## Dependencies

Uses linker hunk globals and `gethunk()` from `obj.c`.

## Risks And Invariants

- Memory is intentionally arena-style and never freed.
- `calloc()` multiplies sizes without overflow checks.
- `realloc()` is unsupported; caller code must not depend on it.
