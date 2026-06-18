# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/error.c

Definitions of fossil's shared error string constants.

The strings cover bad addresses, corrupted labels/entries/meta/superblocks, illegal modes and paths, read-only state, removed files, snapshot errors, Venti I/O, and common file operation failures. They are used with `vtSetError` throughout the cache, file, fs, and checker layers.
