# sources/security-integrity/audit-userspace/src/auditctl-listing.c

Purpose: formats kernel audit status and rule-list replies for `auditctl -s` and `auditctl -l`, including interpreted field/syscall names and watch syntax reconstruction.

Important APIs/functions: `audit_print_init`, `audit_print_reply`, `key_match`; internal helpers `is_watch`, `print_arch`, `print_syscall`, `print_field_cmp`, `print_rule`, `get_enable`, and `get_failure`.

Control flow: list replies are buffered into a local linked list after optional key filtering. On `NLMSG_DONE`, the socket is closed and buffered rules are printed. Rule printing detects watch-style rules, prints action/filter/arch/syscalls, then iterates fields with special handling for string buffers, keys, perms, args, errno exits, fstypes, loginuid/session unset, and interfield comparisons.

State and persistence: static `auparse_state_t *au`, static list `l`, and `printed` state persist within the process. `_audit_elf` is reset/used to interpret syscall names by architecture.

Dependencies and integration: depends on libaudit lookup APIs, `auditctl-llist`, auparse interpretation helpers, `key` and `interpret` globals from `auditctl.c`, and optional io_uring constants.

Risks and test signals: buffer offset accounting for string fields must match kernel `audit_rule_data` layout. Listing output can change with table aliases. Exercise with `auditctl -l`, `auditctl -l -i`, `auditctl -l -k key`, and rules containing watches, dir filters, comparisons, and argument filters.
