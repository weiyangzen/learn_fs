# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtn.S

i386 `crtn` fragment. It supplies the `.init` and `.fini` epilogues.

Both sections execute `leave` and `ret`, matching the `%ebp` frame set up by `crti.S`.
