# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crti.S

SPARC `crti` fragment. It includes NetBSD identity notes and defines `_init` / `_fini` section prologues.

Each prologue uses `save %sp, -96, %sp`, establishing a SPARC register-window frame.
