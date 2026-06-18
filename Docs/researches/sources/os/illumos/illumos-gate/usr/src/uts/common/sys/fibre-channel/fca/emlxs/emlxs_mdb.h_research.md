# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mdb.h

## Purpose

Declares MDB debugger support for the `emlxs` driver.

## Main Definitions

- `DRIVER_NAME` is set to `"emlxs"`.
- Includes MDB and DDI kernel headers: `sys/mdb_modapi.h`, `sys/ddi.h`, `sys/sunddi.h`, plus `kmem` and basic types.
- `MAX_FC_BRDS` is defined as `256`.
- Declares help and dcmd entry points:
  - `void emlxs_msgbuf_help();`
  - `int emlxs_msgbuf(uintptr_t base_addr, uint_t flags, int argc, const mdb_arg_t *argv);`
  - `void emlxs_dump_help();`
  - `int emlxs_dump(uintptr_t base_addr, uint_t flags, int argc, const mdb_arg_t *argv);`

## Integration Notes

This is not part of the runtime adapter path. It is used by the driver’s MDB module to inspect message buffers and dumps.

## Risks and Gotchas

- Function prototypes use old-style empty parameter lists for the help functions, meaning unspecified arguments in C rather than explicit `void`.
- `MAX_FC_BRDS` duplicates the same value used in other driver headers; drift would affect debugger assumptions.
