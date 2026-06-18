# File Research: sources/os/bsd/dragonflybsd/sys/sys/linker.h

Defines kernel linker/KLD interfaces and userland kld syscall ABI. Kernel sections define `linker_file`, `linker_file_ops`, `linker_class`, symbol lookup types, dependency tracking, preload metadata search, ELF relocation helpers, and linker debug macros.

User ABI includes module metadata constants, `kld_file_stat`, `kld_sym_lookup`, and functions `kldload`, `kldunload`, `kldfind`, `kldnext`, `kldstat`, `kldfirstmod`, and `kldsym`. Filesystem relevance is high because VFS implementations are commonly loadable kernel modules registered through this linker/module path.
