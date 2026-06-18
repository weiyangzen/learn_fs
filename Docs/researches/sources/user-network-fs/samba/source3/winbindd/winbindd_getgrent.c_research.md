# sources/user-network-fs/samba/source3/winbindd/winbindd_getgrent.c

## Purpose
Implements async batched `WINBINDD_GETGRENT` for enumerating group records from a client-specific enumeration cursor.

## Important APIs, Types, And Control Flow
`winbindd_getgrent_send()` requires `cli->grent_state`, caps the requested batch at 500 groups, allocates arrays for `struct winbindd_gr` and member databases, and starts `wb_next_grent_send()`. `winbindd_getgrent_done()` loops until no more entries, the batch is full, an error occurs, or `endgrent` freed the cursor. `winbindd_getgrent_recv()` converts each group's member db via `winbindd_print_groupmembers()`, lays out group structs followed by comma-separated member strings in one extra-data blob, and updates offsets and response length.

## State And Persistence
Consumes and may free `cli->grent_state`. Temporary per-group member db contexts are freed after serialization. No persistent database is modified.

## Dependencies And Integration Points
Depends on enumeration helpers `wb_next_grent_*`, `lp_winbind_expand_groups()`, and `winbindd_print_groupmembers()` from `winbindd_group.c`.

## Risks And Test Signals
The packed extra-data layout is sensitive to offset/length mistakes. An empty member database allocates zero bytes and leaves an empty string assumption to consumers. Test zero requested entries, no active cursor, exact batch limit, large member lists, no-more-entries cleanup, and `endgrent` interleaving.
