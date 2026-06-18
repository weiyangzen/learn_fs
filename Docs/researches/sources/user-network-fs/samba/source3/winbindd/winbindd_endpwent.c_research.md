# sources/user-network-fs/samba/source3/winbindd/winbindd_endpwent.c

## Purpose
Implements async `WINBINDD_ENDPWENT`, the end-of-enumeration command for passwd/user iteration. It releases per-client passwd enumeration state.

## Important APIs, Types, And Control Flow
`winbindd_endpwent_send()` allocates a dummy tevent state, logs the command, frees `cli->pwent_state`, completes the request, and posts it to the caller's event context. `winbindd_endpwent_recv()` logs completion and returns `NT_STATUS_OK`.

## State And Persistence
Only `winbindd_cli_state.pwent_state` is cleared. No global cache or persistent database is modified.

## Dependencies And Integration Points
Depends on `winbindd.h` and the user-enumeration state consumed by `wb_next_pwent_send()` in `winbindd_getpwent.c`.

## Risks And Test Signals
Behavior is intentionally idempotent from the client perspective, but interleaving with in-flight `GETPWENT` can invalidate the running enumeration. Test repeated end calls, end without set, end after partial enumeration, and end during a large domain enumeration.
