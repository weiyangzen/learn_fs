# sources/security-integrity/audit-userspace/lib/fstypetab.h

Purpose: Lookup input mapping selected filesystem magic numbers to names for audit filesystem filters.

Important entries: `tracefs`, `debugfs`, `cgroup`, and `cgroup2` magic values from Linux `magic.h`.

Control flow: No runtime logic; generated into `fstypetabs.h` with lower-case lookup helpers.

State and persistence: Static mapping used when parsing/displaying `fstype` audit rule fields.

Dependencies and integration: Used by `audit_name_to_fstype`, `audit_fstype_to_name`, and `AUDIT_FSTYPE` handling in `audit_rule_fieldpair_data`. Requires kernel support for filesystem filter feature bits.

Risks: Small explicit table means unsupported filesystem names are rejected unless numeric values are used. Magic values must stay in sync with Linux headers.

Test signals: Parse `fstype=tracefs` and `fstype=cgroup2`, reverse lookups, and feature-gated filesystem filter tests.
