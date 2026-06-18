# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.c

Implements the interpreter allocator over Ghostscript reference memory spaces. `ialloc_init` creates local, stable-local, system, and optionally distinct global/stable-global memories; Level 1 aliases global to local.

Main services:
- Select current VM space with `ialloc_set_space`.
- Expose memory space, new mask, and save level.
- Reset GC request flags across VM spaces.
- Register ref roots.
- Allocate, shrink, and free ref arrays with special handling for GC terminator refs, LIFO allocation, large chunks, packed arrays, and dangling-reference nulling.
- Allocate string refs.

Key invariant: every run of refs has an extra terminator ref used by the garbage collector. Ref-array free paths either reclaim LIFO/whole-chunk storage or null out contents and account lost bytes.
