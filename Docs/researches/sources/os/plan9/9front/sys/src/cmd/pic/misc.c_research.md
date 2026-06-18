# File Research: sources/os/plan9/9front/sys/src/cmd/pic/misc.c

`misc.c` provides shared geometry, attribute, object allocation, and lookup helpers for `pic`. It maps parser direction tokens to internal direction modes, extracts object components such as `.x`, `.y`, `.wid`, `.ht`, and `.rad`, stores expression lists for `sprintf`, and appends parsed attributes to the global `attr` array.

Position helpers compute named corners, starts/ends, centers, interpolated positions, relative offsets, and block-local references. `getlast()` and `getfirst()` search `objlist`, with special handling to skip block internals. `getblk()` reads a block’s local symbol table.

`makenode()` allocates variable-length `obj` records, initializes them from current drawing state, records text index ranges, grows `objlist` as needed, and appends the object. `extreme()` maintains picture bounding extrema used later for output scaling.
