# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wgetv.c

Purpose: Implements Windows `gp_getenv`, combining process environment lookup with registry fallback for Ghostscript configuration values.

Key interfaces: `gp_getenv` and `gp_getenv_registry`.

Control flow: `gp_getenv` first calls C `getenv`; if found, it either copies the value or reports required buffer length. If absent on Win32, it builds a Ghostscript product/version registry key and checks `HKEY_CURRENT_USER` then `HKEY_LOCAL_MACHINE`. Missing values return 1 with an empty one-byte result contract.

Dependencies: Uses Windows registry APIs, `gscdefs.h` product family/revision globals, `getenv`, and the `gpgetenv.h` contract.

Risks and notes: Registry key and version buffers are fixed-size stack arrays. The code excludes Win32s based on `GetVersion`. It only handles string registry values expected as `REG_SZ`.
