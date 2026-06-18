# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crt0.S

PowerPC process entry stub. On 32-bit builds it initializes small-data register `%r13` from `_SDA_BASE_`.

It moves cleanup from `%r7` to `%r3`, moves `ps_strings` from `%r8` to `%r4`, and calls `___start`.
