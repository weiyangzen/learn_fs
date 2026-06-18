## sources/security-integrity/audit-userspace/src/ausearch-parse.c

Purpose: extracts searchable fields from assembled audit events and provides rotated-log timestamp discovery shared by `ausearch` and `aureport`.

Important APIs/functions: `extract_search_items()` dispatches per-record parsers; `lookup_uid_destroy_list()` clears parser uid cache; `audit_log_list()`, `audit_log_find_start()`, and `audit_log_free()` support rotated log traversal. Internal parsers cover syscall/uring, cwd/path/AVC path, user/login/daemon/kernel/integrity/anomaly/TTY/netfilter/socket records, AVCs, virtual machine fields, keys, hostnames, SELinux contexts, and success/session/exit data.

Control flow: extraction iterates every `lnode` in an `llist`, switches by audit message type, and fills `l->s`. Most parsers only do expensive extraction when the corresponding global filter or report need is set. Many parse routines temporarily NUL-terminate fields inside `n->message`, convert/unescape values, then restore delimiters.

State/persistence: parsed state is stored in `search_items`; cached uid names are in static `nvlist uid_nvl`; a static auparse buffer supports enriched interpretations. Log enumeration allocates an array of `audit_log_info` and reads first timestamps from files.

Dependencies/integration: depends on `libaudit`, `ausearch-options` globals, `ausearch-lookup` unescape, `ausearch-nvpair`, `auparse-idata`, sockets, passwd, and `llist` ownership semantics.

Risks/test signals: this is the highest-risk module. Parsers mutate message buffers, have many format-specific offsets (`NAME_OFFSET`), and can leak or overwrite fields on duplicate records. Conditional parsing means reports may miss fields unless the right globals are set. `audit_log_find_start()` assumes rotated log ordering by first timestamp. Tests should use real audit fixtures plus fuzzed malformed records for every parser return path, hex/unquoted/quoted strings, relative path rebuild with cwd, UNIX/IPv4/IPv6 sockaddr, USER_AVC, multiple AVCs, io_uring, config keys, virtual machine UUID/name, and rotated log start selection.
