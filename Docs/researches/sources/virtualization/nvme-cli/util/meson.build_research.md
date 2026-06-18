# File Research: sources/virtualization/nvme-cli/util/meson.build

## Role

`util/meson.build` defines the utility source files that are included in the nvme-cli build.

## Source Selection

Always included:

- `util/argconfig.c`
- `util/base64.c`
- `util/crc32.c`
- `util/suffix.c`
- `util/types.c`

Windows-only:

- `util/sighdl-win.c`

Non-Windows:

- `util/sighdl-linux.c`
- `util/utils.c`
- `util/table.c`
- `util/dashboard.c`

Conditional on `json_c_dep.found()`:

- `util/json.c`

## Research Notes

This file establishes platform boundaries for this group. The dashboard, table, and generic Linux utility parser code are not part of the Windows build, while suffix and type conversion utilities are shared. JSON implementation is compiled only when json-c is available, matching the `CONFIG_JSONC` behavior in `json.h`.
