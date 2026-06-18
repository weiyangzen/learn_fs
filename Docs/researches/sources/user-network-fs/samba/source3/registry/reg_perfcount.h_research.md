<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_perfcount.h -->
# sources/user-network-fs/samba/source3/registry/reg_perfcount.h

Purpose: Public header for the registry performance counter provider.

Important APIs, types, and functions: Declares `reg_perfcount_get_base_index()`, `reg_perfcount_get_last_counter()`, `reg_perfcount_get_last_help()`, `reg_perfcount_get_counter_help()`, `reg_perfcount_get_counter_names()`, and `reg_perfcount_get_hkpd()`. It includes `reg_parse_prs.h` for `prs_struct`.

Control flow: No executable logic. Callers use the scalar helpers to expose registry metadata values and use `reg_perfcount_get_hkpd()` to marshal performance data into a parse stream.

State and persistence behavior: No header-owned state. Implementations read Samba state TDBs and allocate output buffers for callers.

Dependencies and integration points: Included by registry backend code that serves `HKEY_PERFORMANCE_DATA` and by `reg_perfcount.c`. The API uses Samba `WERROR` and parse-buffer conventions rather than raw Windows structures.

Risks: Callers must free buffers returned through `char **retbuf` according to the implementation's allocation conventions and must handle zero lengths as missing or failed data. `reg_perfcount_get_hkpd()` reports Windows registry errors, while the other functions return byte counts or indexes, so error handling is mixed.

Test signals: Compile coverage for registry modules, plus API-level tests for zero base index, last-counter/help arithmetic, successful name/help buffer ownership, and HKPD insufficient-buffer return mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_perfcount.h -->
