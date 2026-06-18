# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/compat.c

Read fully: 65 lines, 704 bytes. SHA-256 prefix: `d7e14d473640839e`.

This file provides linker-local compatibility shims for allocation and file existence. It overrides `malloc()`, `calloc()`, `free()`, `realloc()`, `mysbrk()`, `setmalloctag()`, and `fileexists()`.

The allocator is a simple bump allocator over linker hunks: `malloc()` rounds to 8-byte alignment, calls `gethunk()` until enough space exists, then advances `hunk` and reduces `nhunk`. `calloc()` zeroes the allocated region. `free()` is a no-op. `realloc()` is deliberately unsupported and aborts if called. `mysbrk()` delegates to `sbrk()`. `fileexists()` uses `stat()` into a fixed buffer and treats any successful stat as existence.

Integration: `obj.c` and the linker’s symbol/program constructors rely on this hunk allocator, so normal libc allocation semantics do not apply inside `kl`.

Risk notes: there is no deallocation and no `realloc()`. This is appropriate for a one-shot linker but unsafe for code that expects general-purpose heap behavior.
