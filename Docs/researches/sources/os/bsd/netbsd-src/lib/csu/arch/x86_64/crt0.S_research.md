# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crt0.S

x86_64 process entry stub. It aligns `%rsp` to 16 bytes, subtracts 8 to satisfy call-frame expectations, moves cleanup from `%rdx` to `%rdi`, and moves `ps_strings` from `%rbx` to `%rsi`.

It jumps directly to common `___start`.
