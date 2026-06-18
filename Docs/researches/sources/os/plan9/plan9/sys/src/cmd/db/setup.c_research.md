# File Research: sources/os/plan9/plan9/sys/src/cmd/db/setup.c

This file initializes symbol and core maps for the debugger.

Key behaviors:
- Maintains `symfil`, `corfil`, `symmap`, `cormap`, `dotmap`, `fsym`, and `fcor`.
- `setsym()` opens the symbol file, cracks its executable header, selects machine type, loads maps, initializes symbols, and records static-base register value if present.
- `setcor()` opens the core/proc memory file and either attaches to a running process or builds text/data mappings from the executable header.
- `dumbmap()` builds a single all-address data segment and defaults the machine to i386 if no machine is set.
- `cmdmap()` lets debugger commands mutate map segment base/end/file offsets.
- `getfile()` opens files read-write with read-only fallback, optionally creating files under write mode.
- `kmsys()` adjusts symbol maps for kernel address layout.
- `attachprocess()` switches `corfil` to `/proc/<pid>/mem`, calls `setcor()`, and warns if `/proc/<pid>/text` does not match the loaded symbol file.

Notable implementation details:
- `setcor()` closes existing core-map segment descriptors before rebuilding.
- `cmdmap()` supports mapping `?` and `/` maps onto each other by sharing `symmap` and `cormap`.
- Kernel remapping uses machine-specific `ktmask` and `kbase`.
