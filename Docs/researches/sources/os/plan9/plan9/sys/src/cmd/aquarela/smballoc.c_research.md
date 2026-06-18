# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smballoc.c

SMB memory allocation helpers.

Key functions:
- `smbemallocz` allocates through `nbemalloc` and optionally zeros memory.
- `smbemalloc` is nonzeroing allocation.
- `smbestrdup` duplicates strings using fatal allocation.
- `smbfree` frees and nils a pointer.
- `smberealloc` wraps `realloc` and asserts success for nonzero sizes.

Interactions:
- Used across SMB code for small structs, strings, and dynamic arrays.

Notable details:
- Under `LEAK`, macros in `smbfns.h` can bypass these wrappers.
