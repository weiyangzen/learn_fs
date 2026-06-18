# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/malloc_.h

`malloc_.h` is Ghostscript's portable wrapper for allocation declarations. It includes `std.h` before any platform header that may include `sys/types.h`.

The header selects the correct allocation header for old compilers and platforms: Turbo C uses `<alloc.h>`, many POSIX/STDC/VMS paths use `<stdlib.h>`, some old BSD-style paths declare `malloc` and `free` manually, and remaining systems use `<malloc.h>`.

It defines `gs_realloc(ptr, old_size, new_size)` as a portability layer. On Linux it declares `gs_realloc` and marks `malloc__need_realloc`; elsewhere it maps directly to `realloc`. The risk is historical platform branching and reliance on old compiler/platform macros.
