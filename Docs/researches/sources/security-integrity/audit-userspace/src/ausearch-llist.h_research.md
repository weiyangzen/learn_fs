## sources/security-integrity/audit-userspace/src/ausearch-llist.h

Purpose: defines the central in-memory event model for `ausearch` and `aureport`.

Important APIs/types: `event` identifies an audit event by seconds, milliseconds, serial, node, and first type. `search_items` stores parsed pid/uid/gid/session/syscall/exit, host, files, cwd, exe, keys, terminal, comm, AVCs, account, uuid/vmname, and interpreted uid strings. `lnode` stores one raw/enriched audit record. `llist` owns a linked list of `lnode`, event identity, parsed fields, and log format.

Control flow/state: `lol_add_record()` populates record lists; `extract_search_items()` fills `search_items`; `match()` and report scanners consume it.

Dependencies/integration: includes `ausearch-string.h`, `ausearch-avc.h`, and `ausearch-common.h`, making this header the major dependency hub.

Risks/test signals: changes to `search_items` require updates to `list_create()` and `list_clear()`. Tests should assert default sentinel values, especially `uid=-1`, `loginuid=-2`, `session_id=-2`, `success=S_UNSET`, and `exit_is_set=0`.
