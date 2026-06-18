# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/pc.c

User-mode platform support for memory estimation and process creation.

Key responsibilities:
- Defines global `Mconf mconf`.
- `mconfinit()` reads `#c/swap` to estimate available user memory; defaults to 64 MB if unavailable.
- Builds one fake memory bank starting at `0x10000000`.
- `meminit()` initializes memory config and returns memory size.
- `procsetname()` writes process name text to `#p/<pid>/args`.
- `newproc()` forks with `RFPROC|RFMEM|RFNOWAIT`, sets child process name, calls the provided function, and exits if it returns.

Research notes:
- The fake memory-bank abstraction preserves old kernel-file-server allocation patterns in user mode.
- `newproc()` shares memory (`RFMEM`), so global locks and queues coordinate all worker processes.
