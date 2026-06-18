## sources/security-integrity/audit-userspace/src/ausearch-match.c

Purpose: applies `ausearch` command-line criteria to a parsed `llist` event.

Important APIs/functions: public `match()` returns 1 for events satisfying all requested criteria. Helpers `load_interpretations()`, `strmatch()`, `user_match()`, `group_match()`, and `context_match()` organize expensive work and criteria groups.

Control flow: `match()` first checks time and event serial, optionally loads interpretations for username filters, calls `extract_search_items()`, then short-circuits through node, user, group, ppid/pid, arch, syscall, session, exit, success, message type, filename/cwd, host, terminal, exe, comm, key, vm name, uuid, and SELinux context checks. Most options are ANDed; `--uid-all` and `--gid-all` OR their related ids; `--context` ORs subject/object context.

State/persistence: no own persistence; reads global search criteria and mutates list cursors. It can trigger interpretation state in `ausearch-report.c`.

Dependencies/integration: depends on globals from `ausearch-options.h`, field extraction from `ausearch-parse.c`, AVC lists, integer/string list cursors, and libaudit machine conversion.

Risks/test signals: parser extraction is conditional on global filters, so adding new filters requires parser updates. Cursor mutation means later output should reset list position. Tests should cover exact vs substring matching, username interpretation filters, combined AND/OR semantics, absent fields, multiple message types, context lists with multiple AVCs, and event_id/time boundaries.
