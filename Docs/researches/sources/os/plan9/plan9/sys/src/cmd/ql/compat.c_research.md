# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/compat.c

Compatibility allocation and filesystem helpers for the PowerPC linker.

Key responsibilities:
- Provides a simple hunk-based `malloc()` aligned to 8 bytes.
- Implements no-op `free()`.
- Implements `calloc()` over the custom allocator.
- Rejects `realloc()` by printing and aborting.
- Wraps `sbrk()` as `mysbrk()`.
- Provides no-op `setmalloctag()`.
- Implements `fileexists()` using `stat()`.

Dependencies:
- Uses linker hunk globals and `gethunk()` from `l.h`.

Notable risks:
- Memory is arena-style and not actually freed.
- Any unexpected caller of `realloc()` aborts the linker.
- Overrides standard allocation names, so behavior differs from normal libc allocation.
