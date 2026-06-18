# sources/security-integrity/audit-userspace/src/auditctl-listing.h

Purpose: public header within the auditctl binary for rule/status listing helpers.

Important APIs/types: declares `audit_print_init`, `audit_print_reply`, and `key_match`, and includes `libaudit.h` for `struct audit_reply` and `struct audit_rule_data`.

Control flow: none; declaration-only header.

State and persistence: none.

Dependencies and integration: included by `auditctl.c` and implemented by `auditctl-listing.c`.

Risks and test signals: prototype drift breaks auditctl build. Build auditctl and exercise list/status commands.
