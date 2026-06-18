# File Research: sources/os/bsd/netbsd-src/lib/csu/common/sysident.S

Common assembly source for NetBSD ELF identity notes. It emits `.note.netbsd.ident` with OS name and `__NetBSD_Version__`, plus `.note.netbsd.pax` with default PaX flags.

If `ELF_NOTE_MARCH_DESC` is defined, it also emits `.note.netbsd.march` with the machine-architecture descriptor. These notes help the kernel identify NetBSD binaries and ABI/machine properties.
