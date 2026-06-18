# sources/user-network-fs/samba/source3/printing/nt_printing_os2.h

Purpose: declares the OS/2 driver-name mapping helper used by spoolss printing code.

Important API: `WERROR spoolss_map_to_os2_driver(TALLOC_CTX *mem_ctx, const char **pdrivername);` accepts an in/out driver-name pointer and may replace it with a talloc-owned mapped OS/2 name.

Control flow and integration: callers pass the current Windows driver name before returning printer information to OS/2-oriented clients. The implementation decides whether a configured mapping file exists and whether the name should change.

State and persistence: no state in the header. The implementation reads a configured map file and caches the last mapping.

Dependencies: requires `WERROR`, `TALLOC_CTX`, and pointer type declarations from Samba headers.

Risks and test signals: caller ownership expectations matter because the returned pointer may become talloc-managed under `mem_ctx` or remain the original string. Tests should verify no caller frees or mutates the replacement incorrectly.
