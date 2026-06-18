# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crt0.S

Alpha process entry stub. It documents the register ABI from the kernel or dynamic loader: `a1` cleanup and `a3` `ps_strings`.

The code loads the global pointer, moves cleanup to `a0`, moves `ps_strings` to `a1`, and calls common `___start`.
