# File Research: sources/os/plan9/9front/sys/src/cmd/db/setup.c

Purpose: Symbol/core file opening and map setup for `db`.

Key behavior:
- `setsym()` opens the symbol file, cracks the executable header, selects machine type, loads text/data maps, initializes symbols, and records static-base register value if available.
- `setcor()` opens the core/process memory file, builds a process map through `attachproc()` when debugging a live pid, or creates text/data maps for static core/image access.
- `dumbmap()` creates a fallback single data map and defaults machine data to i386.
- `cmdmap()` edits map segment base/end/file offsets from debugger commands and can alias symbol/core maps.
- `getfile()` opens or creates files according to debugger mode and handles read-only fallback.
- `kmsys()` adjusts maps for kernel-style addressing.
- `attachprocess()` attaches to a pid specified by address expression and warns if text images differ.

Notable details:
- `setcor()` closes prior map fds before replacing a core map.
- Kernel mapping adjusts text/data using `mach->ktmask` and `mach->kbase`.
