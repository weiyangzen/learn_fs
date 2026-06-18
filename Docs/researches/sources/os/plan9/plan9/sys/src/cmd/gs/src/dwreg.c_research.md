# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwreg.c

Purpose: Win32 registry helper for Ghostscript application settings.

Key functions:
- `win_registry_key`: builds `Software\<gs_productfamily>`.
- `win_get_reg_value`: reads a named `REG_SZ` value from `HKEY_CURRENT_USER`.
- `win_set_reg_value`: opens or creates the Ghostscript key under `HKEY_CURRENT_USER` and writes a named `REG_SZ`.

Usage:
- Used by text/image windows to persist positions and likely other user settings.
- Comments note the product family comes from `gscdefs.h`.

Risks:
- Ignores return from `win_registry_key` in callers.
- Uses fixed 256-byte key buffer.
- In `win_get_reg_value`, `bptr == (char *)NULL` compares a `BYTE *` against a `char *` cast, harmless but untidy.

Filesystem relevance: None directly; registry persistence only.
