# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crt0.S

OR1K process entry stub. It aliases `_start` to `__start` and jumps to `___start`.

The file relies on the platform entry register convention already matching the common startup signature.
