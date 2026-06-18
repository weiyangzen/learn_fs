# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtn.S

x86_64 `crtn` fragment. It restores the stack adjustment with `addq $8, %rsp` and returns.

The same epilogue is emitted for `.init` and `.fini`.
