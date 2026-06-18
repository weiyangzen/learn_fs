# sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-success.rules

Purpose: OSPP successful file creation auditing.

Important rules: six b32/b64 rules for `openat/open_by_handle_at` with `a2&0100`, `open` with `a1&0100`, and `creat`, all with `success=1`, `auid>=1000`, `auid!=unset`, key `successful-create`.

Control flow: loads as specific creation success filters before general successful access rules.

State and persistence: kernel audit exit rules.

Dependencies and integration: relies on arch-specific syscall tables and argument mask parsing.

Risks and test signals: can be high volume on busy systems. Test by creating files as a normal logged-in user and searching `successful-create`.
