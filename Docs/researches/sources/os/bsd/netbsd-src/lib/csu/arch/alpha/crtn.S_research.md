# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtn.S

Alpha `crtn` fragment. It supplies matching epilogues for `.init` and `.fini`.

The code restores GP and return address, releases the 32-byte frame, and returns.
