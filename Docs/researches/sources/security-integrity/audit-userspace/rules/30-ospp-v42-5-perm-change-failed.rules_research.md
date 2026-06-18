# sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-failed.rules

Purpose: OSPP unsuccessful permission and extended-attribute change auditing.

Important rules: four b32/b64 rules for chmod/fchmod/fchmodat/fchmodat2, setxattr/removexattr variants, `setxattrat`, `removexattrat`, and `file_setattr` with `-EACCES` or `-EPERM`, user filters, key `unsuccessful-perm-change`.

Control flow: exit filters grouped by failure code.

State and persistence: kernel audit rules.

Dependencies and integration: depends on syscall availability on the target kernel and architecture.

Risks and test signals: newer syscall names may require new enough audit userspace/kernel; old systems may need `-i` or `-c`. Test denied chmod/xattr operations and key lookup.
