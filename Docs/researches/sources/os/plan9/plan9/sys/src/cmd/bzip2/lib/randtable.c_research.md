# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/randtable.c

Static randomisation table for legacy bzip2 randomised blocks. It defines `Int32 BZ2_rNums[512]`.

Modern compression in this copy always writes the randomised bit as false, but decompression still supports randomised old streams through macros in `bzlib_private.h` that consume this table.
