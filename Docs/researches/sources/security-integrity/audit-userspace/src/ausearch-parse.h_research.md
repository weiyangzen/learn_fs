## sources/security-integrity/audit-userspace/src/ausearch-parse.h

Purpose: public parse/log-enumeration interface for `ausearch` and `aureport`.

Important APIs/types: declares `extract_search_items()`, `lookup_uid_destroy_list()`, `struct audit_log_info { name, sec, milli }`, `audit_log_list()`, `audit_log_find_start()`, and `audit_log_free()`.

Control flow/state: callers assemble an `llist`, call extraction before matching/reporting, and use log enumeration before reading rotated audit log files.

Dependencies/integration: includes `ausearch-llist.h`, so parse output is directly tied to `search_items`.

Risks/test signals: callers must free `audit_log_info` arrays through `audit_log_free()`. Tests should validate zero-log behavior, unreadable logs, empty logs, and timestamp parsing of first records.
