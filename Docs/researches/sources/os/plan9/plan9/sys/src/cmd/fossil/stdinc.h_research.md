# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/stdinc.h

This is the common Fossil include shim. It includes Plan 9 base headers `<u.h>` and `<libc.h>`, defines Venti integer aliases (`u64int`, `u8int`, `u16int`), then includes `oventi.h`, `vac.h`, and `fs.h`.

It centralizes the minimal platform and Fossil/Venti type environment used by the surrounding Fossil C files.
