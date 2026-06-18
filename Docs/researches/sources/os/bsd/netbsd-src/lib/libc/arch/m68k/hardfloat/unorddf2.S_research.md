# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unorddf2.S

Despite the file name, this source defines `__unordsf2`: it performs a single-precision FPU comparison and returns zero when operands are ordered, one otherwise according to the branch-on-ordered condition logic in the file.
