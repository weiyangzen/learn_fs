# File Research: sources/windows/dokany/dokan/dokanc.h

Internal/public control header for Dokan service, debug logging, driver control, and installation helper APIs.

Key responsibilities:
- Defines global device and driver service names using `DOKAN_MAJOR_API_VERSION`.
- Defines service operation constants for start, stop, and delete.
- Declares global debug flags `g_DebugMode` and `g_UseStdErr`.
- Implements static debug print helpers for narrow and wide strings using stack allocation and secure formatting.
- Defines `DbgPrint` and `DbgPrintW` macros for MSVC and GCC builds.
- Defines local `NT_SUCCESS` macro.
- Declares APIs for stderr/debug mode toggles, service install/delete, network provider install/uninstall, driver debug mode changes, and stale mount point cleanup.

Important behavior:
- Debug output goes either to `stderr` or `OutputDebugString[A/W]`.
- `DOKAN_OPTION_STDERR` can force debug output through stderr at runtime in `dokan.c`.
- Formatting failure falls back to outputting the format string.

Dependencies:
- Includes `dokan.h` and `<malloc.h>`.
- Uses `_vscprintf`, `_vscwprintf`, `_malloca`, `_freea`, `OutputDebugString`, and CRT output functions.

Notable risks:
- The debug helpers call `va_start` once and then use the same `va_list` for both sizing and formatting; portable C normally requires `va_copy` or reinitialization after a sizing pass.
- Debug macros depend on compiler-specific variadic macro handling.
- The local `NT_SUCCESS` macro can conflict with other definitions if include ordering changes.
