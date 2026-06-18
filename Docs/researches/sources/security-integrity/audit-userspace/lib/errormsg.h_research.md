# sources/security-integrity/audit-userspace/lib/errormsg.h

Purpose: Defines internal libaudit rule-parser error numbers and printable error message metadata.

Important types and constants: `struct msg_tab` maps error keys to output positioning and message text. `EAU_*` constants cover missing operations, unknown fields/architectures/message types, unsupported filters/features, string length problems, incompatible comparisons, and permission syscall expansion failures. `err_msgtab[]` maps negative error values to diagnostics used by `audit_number_to_errmsg`.

Control flow: Header data is compiled when `NO_TABLES` is not defined. `audit_number_to_errmsg` in `libaudit.c` scans this table and formats messages according to `position`.

State and persistence: Static in-process diagnostic table only.

Dependencies and integration: Tightly coupled to return values from `audit_rule_fieldpair_data`, `audit_rule_interfield_comp_data`, and related parser helpers.

Risks: Error code numbers are reused by callers and diagnostics; comments mark deprecated holes that must not be reused. Missing entries produce silent no-output behavior in `audit_number_to_errmsg`.

Test signals: Parser negative-path tests that assert specific `EAU_*` return values and expected stderr from `audit_number_to_errmsg`.
