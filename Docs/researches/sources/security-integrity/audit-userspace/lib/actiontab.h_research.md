# sources/security-integrity/audit-userspace/lib/actiontab.h

Purpose: Lookup input mapping audit rule actions to textual names.

Important entries: `_S(AUDIT_NEVER, "never")`, `_S(AUDIT_POSSIBLE, "possible")`, and `_S(AUDIT_ALWAYS, "always")`.

Control flow: No runtime logic; consumed by `gen_tables.c` to generate `actiontabs.h`.

State and persistence: Static mapping compiled into libaudit translation functions.

Dependencies and integration: Depends on kernel audit constants from `<linux/audit.h>`. Used by `audit_name_to_action` and `audit_action_to_name` for rule parsing/display.

Risks: The deprecated or less-common `possible` action must remain if kernel/user ABI still exposes it. Text changes affect CLI compatibility.

Test signals: Translation tests for all three action strings and constants, including case behavior from generator flags.
