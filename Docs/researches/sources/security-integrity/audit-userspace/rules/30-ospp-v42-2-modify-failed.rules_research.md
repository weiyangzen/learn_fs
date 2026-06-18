# sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-failed.rules

Purpose: OSPP unsuccessful file modification auditing for write-open and truncate operations.

Important rules: 12 b32/b64 rules cover `openat/open_by_handle_at` and `open` with write/truncate masks, plus `truncate` and `ftruncate`, for `-EACCES` and `-EPERM`, key `unsuccessful-modification`.

Control flow: specific failed modification filters should precede broader failed access rules.

State and persistence: kernel exit filters.

Dependencies and integration: depends on correct octal masks and syscall argument positions.

Risks and test signals: broad write-open masks may be noisy. Test denied write/truncate attempts and search key `unsuccessful-modification`.
