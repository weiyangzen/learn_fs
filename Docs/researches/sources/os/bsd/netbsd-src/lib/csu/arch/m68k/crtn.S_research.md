# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtn.S

m68k `crtn` fragment. It terminates both `.init` and `.fini` with `rts`.

This is the matching epilogue for the minimal labels emitted by `crti.S`.
