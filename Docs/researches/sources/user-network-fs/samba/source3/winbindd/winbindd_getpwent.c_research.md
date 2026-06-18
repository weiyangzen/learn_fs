# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwent.c

## Purpose
Implements async batched `WINBINDD_GETPWENT`, returning up to 500 passwd entries from a client-specific user enumeration cursor.

## Important APIs, Types, And Control Flow
`winbindd_getpwent_send()` checks `cli->pwent_state`, caps requested entries at 500, allocates a `struct winbindd_pw` array, and starts `wb_next_pwent_send()`. `winbindd_getpwent_done()` loops until no more users, batch full, error, or `endpwent` removes the cursor. `winbindd_getpwent_recv()` frees the cursor on errors, returns `NO_MORE_ENTRIES` for empty batches, logs entries, moves the user array into response extra data, and updates `response->data.num_entries` and length.

## State And Persistence
Consumes and may free `cli->pwent_state`. It does not persist anything itself.

## Dependencies And Integration Points
Depends on `wb_next_pwent_send/recv()` and the surrounding setpwent/endpwent command lifecycle.

## Risks And Test Signals
Packed output is a raw array of `struct winbindd_pw`, so ABI expectations matter between daemon and client library. Test zero requested entries, inactive cursor, large domains with multiple batches, no-more cleanup, NSS enumeration-disabled behavior through setup path, and `endpwent` interleaving.
