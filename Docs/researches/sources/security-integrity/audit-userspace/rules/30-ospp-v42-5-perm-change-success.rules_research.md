# sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-success.rules

Purpose: OSPP successful permission and xattr change auditing.

Important rules: b32 and b64 rules for chmod and xattr modification families with `success=1`, user auid filters, key `successful-perm-change`.

Control flow: loaded as exit rules for success path coverage.

State and persistence: kernel audit rules.

Dependencies and integration: requires syscall tables that include newer `fchmodat2`, `setxattrat`, `removexattrat`, and `file_setattr`.

Risks and test signals: high sensitivity to kernel/userspace version skew. Test with successful chmod/setxattr and search key `successful-perm-change`.
