# sources/user-network-fs/samba/source3/modules/vfs_readonly.c

## Purpose
`vfs_readonly.c` makes a share read-only during a configured date/time window. It is a connection-time policy module that parses human-readable date expressions using `get_date()`.

## Important APIs, Types, And Functions
- `readonly_connect()` reads `readonly:period`, delegates connect, parses begin/end times, sets `conn->read_only`, and clears the VUID cache.
- `vfs_readonly_fns` registers only `.connect_fn`.
- Default period is `"today 0:0:0","tomorrow 0:0:0"`, which effectively makes the share read-only for the current day if no parameter is supplied.

## Control Flow
After successful downstream connect, the module obtains a two-element period list from the module parameter namespace, with `handle->param` override support. It compares `time(NULL)` to parsed begin/end values. If current time is within the interval, it sets `handle->conn->read_only = True` and invalidates cached VUID entries so later access decisions re-evaluate read-only state.

## State And Persistence
State is per connection in `connection_struct`. It does not persist to disk. VUID cache entries are cleared in memory to avoid stale write permissions.

## Dependencies And Integration Points
It depends on Samba loadparm list parsing, `getdate.h`, connection read-only enforcement, and Samba's VUID cache layout. It registers as `readonly`.

## Risks
- Date parsing failures are not explicitly checked; invalid expressions may produce unexpected `time_t` values.
- The default period can surprise administrators by making the share read-only unless overridden.
- The policy is evaluated only at connect time; long-lived connections do not automatically flip when the time window starts or ends.

## Test Signals
- Connect inside and outside a configured period and verify write access decisions.
- Verify VUID cache entries are invalidated after enabling read-only.
- Test invalid, missing, and single-element `readonly:period` lists.
- Test multiple stacked instances using different `handle->param` names.
