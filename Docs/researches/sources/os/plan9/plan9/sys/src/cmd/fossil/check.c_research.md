# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/check.c

Filesystem checker used by `flchk` and repair-oriented callers.

It first walks block graphs by epoch, starting from each root block, validating epoch interval rules, active-tree uniqueness, copy-on-write join constraints, labels, entries, pointer blocks, and leaks. It then walks the directory/source tree to verify metadata blocks, sorted directory entries, source references, source generations, file data accessibility, and unreferenced source entries.

The checker is callback-driven: callers provide print and repair hooks for clearing bad entries, clearing pointers, closing blocks, or removing directory entries. The default hooks are no-ops, so this file is both diagnostic engine and repair-script generator backend.
