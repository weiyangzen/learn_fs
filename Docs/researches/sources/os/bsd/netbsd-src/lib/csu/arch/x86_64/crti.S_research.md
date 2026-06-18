# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crti.S

x86_64 `crti` fragment. It includes NetBSD identity notes and defines `_init` / `_fini`.

Each prologue subtracts 8 from `%rsp`, creating the stack adjustment paired by `crtn.S`.
