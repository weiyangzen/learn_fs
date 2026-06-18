# sources/user-network-fs/samba/source3/lib/errmap_unix.c

Purpose: maps Unix `errno` values to NTSTATUS for Windows-compatible error reporting.

Important APIs/types/functions: static `unix_nt_errmap[]` and `map_nt_error_from_unix(int unix_error)`.

Control flow: the mapper linearly scans known errno entries and returns a default NTSTATUS when no entry matches. Conditional errno entries preserve portability.

State/persistence behavior: pure static mapping table; no mutable state.

Dependencies/integration: used by messaging, tevent wrappers, dbwrap watch, and syscall conversion code.

Risks/test signals: incorrect mappings affect SMB-visible behavior. Tests should cover common errno values, platform-conditional values, and unknown fallback.
