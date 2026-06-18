# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crt0.S

SH3 process entry stub. It adapts older kernel `setregs()` argument placement to the modern two-argument `___start`.

Cleanup is moved from `r7` to `r4`, `ps_strings` from `r9` to `r5`, and control jumps through a local datum for `___start`.
