# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crt0.S

EABI ARM process entry stub. It rearranges `ps_strings` and cleanup into the common `___start` argument order.

It aligns the stack differently for ARM and Thumb mode: ARM uses `bic sp, sp, #7`, while Thumb computes the aligned value through temporary registers.
