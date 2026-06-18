# File Research: sources/os/bsd/dragonflybsd/sys/sys/kinfo.h

Defines public/kernel information structures for files, CPU time, PC tracking, clock info, LWPs, processes, and signal trampoline ranges. Major structures are `kinfo_file`, `kinfo_cputime`, `kinfo_pcheader`, `kinfo_pctrack`, `kinfo_clockinfo`, `kinfo_lwp`, `kinfo_proc`, and `kinfo_sigtramp`.

Filesystem relevance: `kinfo_file` reports file descriptor state including fd number, file pointer, type, offset, flags, and backing data pointer. `kinfo_proc` includes jail id, process credentials, VM size, and embedded LWP state. Kernel fill helpers populate these exported snapshots.
