# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/db.c

Implements Plan 9 `ndb` parsing for `/lib/vgadb`-style controller and monitor definitions. It opens databases, builds linked `Attr` lists, looks up attribute values, and creates per-VGA linked copies of controller descriptors from `ctlrs[]`.

`dbctlr` identifies hardware by BIOS strings or PCI IDs, preferring BIOS matches over PCI matches, then saves controllers, RAMDACs, clocks, hwgc modules, linear settings, memory bandwidth, and additional attributes into `Vga`.

`dbmode` and `dbmonitor` resolve monitor timings, aliases, includes, size/depth parsing, optional `@NMHz` clock overrides, sync/interlace flags, and inherited video bandwidth. `dbdumpmode` prints the resolved `Mode`.
