## sources/security-integrity/audit-userspace/src/ausearch-llist.c

Purpose: event-level linked list for audit records plus parsed searchable fields.

Important APIs/functions: `list_create()` initializes `llist` event/search state; `list_append()` shallow-transfers a record message/interp into a new `lnode`; `list_last()`, `list_next()`, `list_prev()`, `list_find_item()`, `list_find_msg()`, and `list_find_msg_range()` navigate records; `list_clear()` frees record messages and parsed search data; `list_get_event()` copies timestamp identity.

Control flow: `ausearch-lol.c` creates one `llist` per audit event and appends all records with matching timestamp/serial/node. Parser modules fill `l->s` after assembly. Matchers and reporters traverse by record type or item number.

State/persistence: no persistence. `llist` owns `lnode.message`, event node string, parsed strings, nested `slist`/`alist` allocations, and interpreted uid strings.

Dependencies/integration: includes string, AVC, common, and auditd config definitions. Used by nearly every file in this work item.

Risks/test signals: `list_prev()` relies on `item` numbering and calls `list_find_item()`, making reverse traversal O(n^2). `list_get_event()` omits node/type. `list_clear()` frees many optional fields and must remain synchronized with `search_items`. Tests should cover clear after every parser path, reverse output order, empty lists, and mixed enriched/raw records.
