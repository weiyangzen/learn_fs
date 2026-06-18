# File Research: sources/os/plan9/9front/sys/src/cmd/mk/fns.h

Declares mk’s cross-file function interface.

Key behavior:
- Covers rule parsing/storage, variable substitution, word lists, graph construction, job scheduling, archive/file times, Plan 9 execution, environment export, shell quoting, and debug dumps.
- Exposes OS-dependent hooks such as `readenv`, `execsh`, `pipecmd`, `waitfor`, `chgtime`, and `mkmtime`.
- Exposes core data constructors like `newarc`, `newjob`, `newword`, and `newbuf`.

Important dependencies: `mk.h` types `Word`, `Rule`, `Node`, `Arc`, `Job`, `Bufblock`, `Symtab`.

Notable risks:
- The header encodes broad global coupling; changing one signature affects most of mk.
