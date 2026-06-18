# File Research: sources/os/plan9/plan9/sys/src/9/bcm/dat.h

BCM/ARM kernel data definitions.

Key contents:
- Defines clock constants (`HZ`, `MS2HZ`, `TK2SEC`, `Mhz`).
- Declares core kernel structs and typedefs used by this port.
- Defines `Lock`, `Label`, floating-point save state (`FPsave`), memory config (`Confmem`, `Conf`), MMU state (`MMMU`, `PMMU`), and per-CPU `Mach`.
- `Mach` contains scheduler, alarm, interrupt, MMU, timing, performance, FPU, and exception scratch fields.
- Defines fake `kmap()`/`kunmap()` for this direct-mapped kernel.
- Declares `active` shutdown state and global machine pointers.
- Defines parsed ISA-style device config structures and debug macros.

The file includes `../port/portdat.h`, binding BCM-specific machine state to shared Plan 9 port data.
