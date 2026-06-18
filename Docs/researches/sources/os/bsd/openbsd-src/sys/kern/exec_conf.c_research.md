# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_conf.c

Exec format registration and initialization.

Key behavior:
- Defines `execsw[]` with two executable formats:
  - shell scripts via `exec_script_makecmds`
  - ELF binaries via `exec_elf_makecmds`
- Exports `nexecs` and `exec_maxhdrsz`.
- `init_exec()` computes the maximum required executable header size from registered formats.

Filesystem/OS relevance:
- Connects `execve` format probing to script and ELF loaders.
