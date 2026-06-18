# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/data.c

Global controller registry for the Plan 9 VGA utility.

Core behavior:
- Defines global flags:
  - `cflag`: do not use hardware graphics cursor.
  - `dflag`: do palette handling.
- Defines `ctlrs[]`, the ordered list of all available `Ctlr` backends: controllers, RAMDACs, clocks, hardware cursors, software cursor, VESA, VMware, Radeon, Nvidia, Matrox, and the files in this group.
- Defines `dacxreg[4]`, mapping low two bits of indirect DAC register addressing to VGA DAC ports.

Dependencies and integration:
- `db.c` uses `ctlrs[]` to instantiate configured controller chains from `vgadb`.
- Many controller modules export `Ctlr` globals consumed here.

Notable risks:
- Registry requires every referenced `Ctlr` symbol to be linked in the build.
- Controller matching in `db.c` depends on names matching this table.
