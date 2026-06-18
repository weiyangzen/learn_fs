# File Research: sources/os/linux/linux-stable/fs/nls/nls_ucs2_data.h

Purpose: Header declaring shared UCS-2 uppercase conversion table data for NLS UCS-2 helpers.

Core structures and data:
- Defines `struct UniCaseRange` with `wchar_t start`, `wchar_t end`, and a signed offset `table`.
- Declares `NlsUniUpperTable[512]`, the base uppercase offset table.
- Declares `NlsUniUpperRange[]`, the range table used for Unicode pages beyond the base table.

Important behavior:
- This header contains no executable logic; it is a declaration boundary between `nls_ucs2_utils.c` and inline consumers in `nls_ucs2_utils.h`.

Dependencies and interfaces:
- Uses `wchar_t`; callers include this through `nls_ucs2_utils.h`.

Design notes and risks:
- The `table` pointer is non-const `signed char *` even though the exported range table points at static data; this matches existing usage but should be preserved carefully for ABI/source compatibility.
