# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.c

## Role
Win32 registry helper for Ghostscript application settings.

## Contents
- Builds a registry key path under `Software\<gs_productfamily>`.
- Reads named string values from `HKEY_CURRENT_USER`.
- Writes named string values under `HKEY_CURRENT_USER`, creating the product key if needed.
- Mimics `gp_getenv`-style return behavior for value lookup: `0` found/copied, `-1` buffer too small, `1` not found.

## Important Interfaces
- `win_registry_key`.
- `win_get_reg_value`.
- `win_set_reg_value`.

## Dependencies And Coupling
- Includes Win32 registry APIs and `gscdefs.h` for `gs_productfamily`.
- Declared by `dwreg.h`; used by `dwmain.c` and `dwimg.c`.

## Risks And Notes
- `win_registry_key` return value is ignored by callers inside this file.
- Uses fixed 256-byte key buffers.
- Registry values are per-user, unlike installer registry entries that are under HKLM.

## Filesystem Relevance
None directly; stores window positions and settings outside the filesystem.
