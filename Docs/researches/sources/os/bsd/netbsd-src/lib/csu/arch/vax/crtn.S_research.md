# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtn.S

VAX `crtn` fragment. It terminates both `.init` and `.fini` with `ret`.

This matches the simple procedure entry masks emitted by `crti.S`.
