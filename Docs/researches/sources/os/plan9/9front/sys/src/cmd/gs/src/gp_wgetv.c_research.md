# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wgetv.c

Purpose: MS Windows implementation of `gp_getenv`.

Key behavior: `gp_getenv` first checks the process environment. It follows the Ghostscript buffer contract: return `0` when copied, `-1` when present but buffer is too small, and `1` when missing.

Registry fallback: On Win32, excluding Win32s, it builds `Software\<gs_productfamily>\<revision>` and checks `HKEY_CURRENT_USER` then `HKEY_LOCAL_MACHINE`. `gp_getenv_registry` reads a named `REG_SZ` value and maps Windows registry return codes to the same buffer contract.

Dependencies and notes: Uses Windows registry APIs, `gscdefs.h` product metadata, and standard `getenv`. Missing values clear the caller buffer to an empty string when possible.
