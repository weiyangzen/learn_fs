# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtn.S

SPARC64 `crtn` object. It emits aligned `ret; restore` epilogues for `.init` and `.fini`, closing the frames opened by `crti.S`.
