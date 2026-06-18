<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setpwent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_setpwent.c

## Purpose
This file implements the asynchronous `WINBINDD_SETPWENT` command, resetting per-client passwd enumeration state before `GETPWENT` calls.

## Important APIs, Types, And Functions
The public entry points are `winbindd_setpwent_send()` and `winbindd_setpwent_recv()`. The private state contains only a dummy byte because the command is immediately posted as complete.

## Control Flow
`send()` creates a tevent request, frees prior `cli->pwent_state`, logs client metadata and `winbind enum users`, and either completes without allocation when enumeration is disabled or allocates a new `struct getpwent_state` under the client. `recv()` always returns OK after logging.

## State And Persistence Behavior
Only `cli->pwent_state` is changed, and it is per-client memory. There is no persistent storage or cross-client state.

## Dependencies And Integration Points
It depends on tevent/talloc, `winbindd.h`, and the `lp_winbind_enum_users()` configuration. It feeds user enumeration through NSS and the varlink `GetUserRecord` enumeration path.

## Risks And Test Signals
The main risk is surprising "success with no enumeration state" when user enumeration is disabled. Tests should cover `SETPWENT` followed by `GETPWENT`, disabled enumeration, and cleanup through `ENDPWENT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setpwent.c -->
