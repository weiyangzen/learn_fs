# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/db.c

NDB-backed VGA configuration database reader. It resolves controller chains and display modes from Plan 9 `vgadb`-style databases.

Core behavior:
- Opens an NDB database and errors on failure.
- Matches controllers by BIOS string offsets/ranges or PCI vendor/device IDs.
- BIOS match wins over PCI match.
- Saves attributes into `Vga`: controller, RAMDAC, clock, hardware cursor, linear address, memory bandwidth, and arbitrary attributes.
- Adds linked copies of `Ctlr` definitions from global `ctlrs[]`, preserving suffixes such as speed grades.
- Parses monitor/mode entries, including aliases and `include` chains.
- Allows mode string clock override in `XxYxZ@NMHz`.
- Provides `dbdumpmode()` debug output.

Important functions:
- `dbctlr()` resolves hardware/controller config.
- `dbmode()` resolves monitor mode timing.
- `dbmonitor()` fills `Mode` fields.
- `dbbios()` and `dbpci()` implement hardware matching.

Dependencies and integration:
- Uses `<ndb.h>`, PCI probing, BIOS reads from `io.c`, and `Ctlr` registry from `data.c`.

Notable risks:
- Include depth guard is fixed at 5.
- Numeric parsing is permissive.
- BIOS matching scans offsets and may read substantial BIOS ranges through `readbios()`.
