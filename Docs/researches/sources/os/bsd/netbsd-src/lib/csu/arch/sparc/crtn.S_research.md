# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtn.S

SPARC `crtn` fragment. It emits matching `.init` and `.fini` epilogues.

Each epilogue uses `ret` with `restore` in the delay slot.
