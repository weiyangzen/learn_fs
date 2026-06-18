# sources/security-integrity/audit-userspace/lib/permtab.h

Purpose: maps audit permission categories to syscall-name sets used by permission-based audit rules. Categories are `AUDIT_PERM_EXEC`, `AUDIT_PERM_WRITE`, `AUDIT_PERM_READ`, and `AUDIT_PERM_ATTR`.

Important APIs/types: consumed by generated `perm_s2i` and `perm_i2s`, surfaced internally as `audit_name_to_perm` and `audit_perm_to_name`.

Control flow: static expansion only. The strings are comma-separated syscall groups used by libaudit rule expansion logic.

State and persistence: none.

Dependencies and integration: documented as sourced from generic audit headers and architecture audit code. Used by libaudit permission parsing and tested by lookup table tests when built.

Risks and test signals: permission groups are policy-sensitive; stale syscall membership can create audit gaps or noisy over-auditing. The direct test signal is lookup round-trip, but semantic completeness must be reviewed against kernel audit permission definitions.
