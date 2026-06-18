# sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-success.rules

Purpose: OSPP successful file access catch-all for open-like syscalls.

Important rules: b32 and b64 rules for `open`, `openat`, `openat2`, and `open_by_handle_at` with `success=1`, user auid filters, key `successful-access`.

Control flow: comments warn it must go last and may generate many events.

State and persistence: kernel exit filters.

Dependencies and integration: parsed by auditctl with syscall and arch lookup support.

Risks and test signals: very high event volume on active systems. Test by opening files and searching key `successful-access`, preferably in a controlled environment.
