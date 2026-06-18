# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fw.h

Purpose: Defines firmware image identifiers, firmware descriptors, firmware module path, and optional static firmware table construction.

Key definitions:
- `EMLXS_FW_MODULE` resolves to `misc/<driver>/<driver>_fw`.
- `emlxs_fwid_t`: firmware IDs for LP10000, LP11000, LP11002, LPe11000, LPe11002, and LPe12000; `FW_NOT_PROVIDED` is zero.
- `emlxs_firmware_t`: firmware descriptor with ID, size, image pointer, label, kernel/stub/SLI1/SLI2/SLI3/SLI4 revision fields.
- `EMLXS_FW_TABLE_DEF` causes firmware-table definition in local memory.
- `EMLXS_FW_IMAGE_DEF` causes firmware images to be defined in the firmware table; it is forced when `MODFW_SUPPORT` is absent.
- Optional table includes adapter-specific firmware headers and builds `EMLXS_FW_TABLE`.

Dependencies and interactions:
- `emlxs_extern.h` declares firmware table globals and optional module firmware load/unload routines.
- `emlxs_fc.h` stores firmware module handle when `MODFW_SUPPORT` is enabled.
- Firmware download/parsing support is further described by firmware image structures in `emlxs_hw.h`.

Implementation notes:
- The table macro is compile-time data assembly, not executable logic.
- One LP11000 table initializer has a trailing comma after `sli4`, which is valid C initializer syntax.
