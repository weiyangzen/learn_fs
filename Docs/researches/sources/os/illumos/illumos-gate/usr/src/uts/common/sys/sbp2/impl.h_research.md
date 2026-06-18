# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/impl.h

## Role

SBP-2 implementation-private helper header for Config ROM parsing and bus operation dispatch macros.

## Key Elements

- `sbp2_cfgrom_parse_arg_t` carries parser recursion state: current directory, parent directory, referred entry, and depth.
- `sbp2_cfgrom_ent_by_key_t` carries lookup criteria and result state for Config ROM entry searches.
- Defines parser limits and defaults:
  maximum Config ROM depth, directory entry growth increment, minimum/default management ORB timeout, and minimum/default ORB size.
- Defines macro wrappers for every `sbp2_bus_t` operation, including CSR base, Config ROM address, interrupt cookie, node ID, buffer alloc/free/sync, read/write completion, command alloc/free, and quadlet/block read/write.
- Declares `sbp2_cfgrom_parse()` and `sbp2_cfgrom_free()`.

## Dependencies and Coupling

Includes common, bus, and driver SBP-2 headers. The bus macros assume a valid `sbp2_tgt_t *` with populated `t_bus` and `t_bus_hdl`.

## Research Notes

This file exists to keep implementation code concise and to centralize the bus-provider dispatch layer. Config ROM parsing is bounded by a fixed recursion depth.
