# File Research: sources/os/bsd/netbsd-src/lib/csu/common/crt0-common.c

Common C startup implementation called by all architecture `crt0.S` stubs. It receives loader cleanup and `ps_strings`, initializes `environ`, `__ps_strings`, and `__progname`, calls libc initialization, runs static preinit/init arrays, registers finalizers, and exits with `main(argc, argv, environ)`.

It handles static IFUNC relocation repair for RELA targets (`__rela_iplt`) and REL targets (`__rel_iplt`), and implements x86/x86_64 self-relocation for static PIE-style binaries using program headers, dynamic tags, RELR, REL/RELA, and relative relocations.

For profiling builds (`MCRT0`) it registers `_mcleanup` and calls `monstartup`. It treats missing `ps_strings` as fatal and writes directly with `SYS_write`.
