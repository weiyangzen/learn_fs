# sources/user-network-fs/samba/source3/winbindd/wb_next_grent.c

Purpose: drives one step of `getgrent` enumeration across winbind domains, returning the next group entry and its member database.

Important APIs and types: `wb_next_grent_send/recv`; `struct wb_next_grent_state`; shared `struct getgrent_state` from `winbindd.h`. It uses `wb_query_group_list_send`, `wb_getgrsid_send`, and `dcerpc_wbint_NormalizeNameMap_send`.

Control flow: `wb_next_grent_send_do` obtains the current domain from a `winbindd_domain_ref`. If current group's list is exhausted, it frees the old list, advances to `wb_next_domain`, and fetches a new group list. If a group is available, it calls `wb_getgrsid_send` for the group's SID. Lookup returning `NT_STATUS_NONE_MAPPED` is skipped and enumeration continues. A successful group lookup is passed through `NormalizeNameMap`; the callback chooses the mapped full name, renamed name, or original domain/name pair, fills `winbindd_gr`, increments `next_group`, and completes.

State and persistence: enumeration cursor state is external in `getgrent_state`: current domain ref, group array, count, and next index. The request owns temporary lookup results and moves the member `db_context` to the caller on receive.

Dependencies and integration points: integrated with NSS `getgrent` handlers, group query wrapper, SID-to-group lookup, idmap child name normalization, and domain iteration. Uses passdb/machine SID context indirectly through included winbind domain logic.

Risks: errors fetching a domain group list are logged and treated as an empty domain, so backend outages can look like end-of-domain rather than hard failures. Name normalization result handling has three status paths that affect visible group names. Member database ownership must be moved exactly once. Stale domain refs terminate with no-more-entries.

Test signals: enumerate across multiple domains, empty/erroring domains, unmapped group SIDs that should be skipped, `NormalizeNameMap` OK/FILE_RENAMED/fallback statuses, member DB transfer, and end-of-enumeration `NT_STATUS_NO_MORE_ENTRIES`.
