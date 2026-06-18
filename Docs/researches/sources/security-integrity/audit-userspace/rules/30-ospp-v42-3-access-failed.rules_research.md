# sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-failed.rules

Purpose: OSPP unsuccessful file access catch-all for open-like syscalls not already classified as create/modify.

Important rules: four b32/b64 rules for `open`, `openat`, `openat2`, and `open_by_handle_at` with `-EACCES` or `-EPERM`, user auid filters, key `unsuccessful-access`.

Control flow: comments state it must go last among access/create/modify groups to preserve more specific keys.

State and persistence: kernel exit filters.

Dependencies and integration: relies on first-match audit rule behavior and open syscall table entries.

Risks and test signals: if loaded too early it can shadow create/modify failure keys. Test with denied read/open and ausearch key `unsuccessful-access`.
