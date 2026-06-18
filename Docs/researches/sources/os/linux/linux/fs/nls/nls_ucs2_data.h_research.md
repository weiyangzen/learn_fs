# File Research: sources/os/linux/linux/fs/nls/nls_ucs2_data.h

Purpose: Header declaring shared UCS-2 uppercase conversion table data for NLS UCS-2 helpers.

Core structures and data:
- Defines `struct UniCaseRange` with `wchar_t start`, `wchar_t end`, and `signed char *table`.
- Declares `NlsUniUpperTable[512]`.
- Declares `NlsUniUpperRange[]`.

Important behavior:
- Contains no executable logic.
- Provides the declaration boundary between `nls_ucs2_utils.c` and inline consumers in `nls_ucs2_utils.h`.

Dependencies and interfaces:
- Uses `wchar_t`; included through `nls_ucs2_utils.h`.

Design notes and risks:
- `table` is a non-const `signed char *` even though range table entries point at static data; this is part of the existing source contract.
