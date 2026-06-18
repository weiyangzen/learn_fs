# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/compat.c

Compatibility allocation shim for the Plan 9 C compiler. It includes `cc.h` and `"compat"`, then redirects standard allocation calls to the compiler arena allocator.

`malloc` and `calloc` call `alloc`; `free` is a no-op; `realloc` prints an error and aborts. `mallocz` allocates with optional zeroing and exists for profiling support. `setmalloctag` is a no-op.

The file makes code expecting libc allocation APIs work inside the compiler’s non-freeing hunk allocator model.
