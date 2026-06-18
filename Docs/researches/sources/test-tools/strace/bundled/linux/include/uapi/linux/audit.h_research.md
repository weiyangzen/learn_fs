<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/audit.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/audit.h

Purpose: Linux audit UAPI constants and structures used for audit netlink command/event decoding and seccomp architecture identifiers.

Important APIs/types: defines audit message number ranges and many `AUDIT_*` command/event constants, filter flags/actions, rule fields/operators, status masks, feature bitmaps, failure actions, architecture encoding bits, `AUDIT_ARCH_*` constants for many ELF machines, permissions, netlink groups, and structures `audit_status`, `audit_features`, `audit_tty_status`, and variable-length `audit_rule_data`.

Control flow: preprocessor constants and enum declarations only. Macros such as `AUDIT_WORD`, `AUDIT_BIT`, `audit_feature_valid`, and `AUDIT_FEATURE_TO_MASK` encode simple calculations.

State and persistence: compile-time ABI definitions for user/kernel audit communication.

Dependencies and integration: includes `<linux/types.h>` and `<linux/elf-em.h>`. Strace uses these for audit netlink, seccomp arch checks, and symbolic decoding.

Risks: large constant surface changes over kernel versions; stale snapshots lead to unknown audit messages or architectures. Variable-length `audit_rule_data.buf[]` requires careful decoder bounds. Test signals: audit netlink decoder tests and seccomp tests should recognize current `AUDIT_ARCH_*` and event constants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/audit.h -->
