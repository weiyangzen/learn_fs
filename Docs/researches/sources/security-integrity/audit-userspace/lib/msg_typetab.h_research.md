# sources/security-integrity/audit-userspace/lib/msg_typetab.h

Purpose: `_S(audit_type, name)` source table for translating kernel audit record type constants to stable audit log names. It covers user, daemon, syscall, path, SELinux/AppArmor, integrity, anomaly, crypto, virtualization, and newer event types such as `URINGOP`, `OPENAT2`, and device-mapper records.

Important APIs/types: consumed by generated `msg_type_s2i` and `msg_type_i2s`, surfaced as `audit_name_to_msg_type` and `audit_msg_type_to_name`. Commented-out entries document intentionally omitted or daemon-filtered/deprecated types.

Control flow: static table expansion only. The surrounding lookup code falls back to decimal and `UNKNOWN[n]` parsing when this table has no match.

State and persistence: no mutable state. Build-time feature macro `WITH_APPARMOR` controls AppArmor entries.

Dependencies and integration: included by `lookup_table.c` and directly by `lookup_test.c`. Consumers include audit log parsers, rule listing for `msgtype`, and audit report tools.

Risks and test signals: missing new kernel record types cause numeric/unknown output rather than symbolic names. Reverse lookup ambiguity is low because names are unique. `lookup_test.c` verifies every included entry round-trips.
