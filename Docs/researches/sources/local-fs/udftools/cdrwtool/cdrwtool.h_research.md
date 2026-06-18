# File Research: sources/local-fs/udftools/cdrwtool/cdrwtool.h

Shared declarations and data layouts for `cdrwtool`.

Defines:
- Default CD-ROM device path: `/dev/scd1`.
- Command wait timeouts for packet commands, sync, blank/format.
- Immediate-operation policy macros.
- Blank modes, write modes, CD-ROM block size, packet size, and default speed.
- `write_params_t`, representing MMC write-parameter page fields.
- `struct cdrw_disc`, the CLI/runtime state for device actions and embedded `struct udf_disc`.

Packed-ish drive data structures:
- `disc_info_t`
- `track_info_t`
- `opc_table_t`
- `disc_capacity_t`

The disc and track info structures use endian-sensitive bitfield layouts gated by `WORDS_BIGENDIAN`.

Exports all cdrwtool operations used by `main.c` and `options.c`, including mode sense/select, blank/format, write, reserve/close, speed, info printing, and initialization.

Key role: bridges user options, Linux cdrom packet commands, and UDF generation state.
