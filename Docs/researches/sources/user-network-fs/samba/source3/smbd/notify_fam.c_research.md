# sources/user-network-fs/samba/source3/smbd/notify_fam.c

## Purpose
`notify_fam.c` provides optional FAM/Gamin-backed system notification integration for smbd. It opens a single process-wide FAM connection, registers directory monitors for a subset of Windows notify filters, converts FAM events into Samba `notify_event` actions, and falls back silently to other notify mechanisms when FAM is unavailable.

## Important APIs, Types, And Functions
`struct fam_watch_context` stores a FAM request, the Samba sys notify context, callback, private data, filter mask, and watched path. Static state includes the singleton `FAMConnection fam_connection`, `fam_connection_initialized`, and `fam_notify_list`. `fam_open_connection()` opens FAM with a process-name string, optionally sets Gamin-specific client options, registers the FAM fd with tevent, and returns NTSTATUS. `fam_reopen()` closes and reopens the singleton connection and reissues monitors. `fam_handler()` drains FAM events and dispatches supported event codes. `fam_watch_context_destructor()` cancels a monitor and removes it from the list. The exported `fam_watch()` installs a watch and returns a talloc handle.

## Control Flow
`fam_watch()` first intersects the requested filter with the FAM-supported mask of file and directory name changes. If none are requested, it returns success with no handle and leaves the filters for other backends. On first use it opens the singleton connection; failure also returns success so smbd can rely on non-FAM notification. A watch object is allocated, path/callback/filter fields are set, handled filter bits are removed from `*filter`, the watch is linked into `fam_notify_list`, and `FAMMonitorDirectory()` is called if the connection fd is valid. If not, `fam_reopen()` attempts to restore all watches.

When tevent signals readability, `fam_handler()` calls `FAMPending()` and `FAMNextEvent()`. A read error frees the fd event and reopens the connection. Supported codes map `FAMChanged` to modified, `FAMCreated` to added, and `FAMDeleted` to removed; other FAM events are ignored. It finds the matching watch by comparing `FAMRequest`, derives the relative path from the event filename, and calls the stored Samba callback with `UINT32_MAX` as the filter.

## State And Persistence
All state is in memory. The FAM connection is singleton per smbd process. Watch lifetimes are controlled by talloc handles returned to callers. The destructor cancels monitor state in FAM when the connection fd is valid and removes the watch from the global list. No events or watches are persisted across process restart.

## Dependencies And Integration Points
This file depends on FAM/Gamin headers and library behavior, tevent fd registration, Samba notify action constants, talloc lifetime management, and the generic sys notify callback signature from smbd. It only handles file/directory name filters and deliberately leaves other filters to notifyd or polling mechanisms by clearing only its supported bits.

## Risks
FAM implementations differ, so the code avoids non-SGI extensions except guarded Gamin calls. Connection reopen must not lose live watch registrations. The global singleton means errors affect all watches. Event path parsing only looks for backslash separators before falling back to the full filename. Returning success when FAM is unavailable is intentional but can hide lack of kernel/system notification coverage if no other backend handles the remaining filters.

## Test Signals
Tests should cover ignored filters, first-open failure fallback, successful watch registration clearing only name-change bits, destructor cancellation/list removal, FAM changed/created/deleted mappings, ignored event codes, unknown request discard, event fd read error and reopen, re-monitoring all watches after reopen, Gamin `FAMNoExists` guarded behavior, and multiple watches sharing the singleton connection.
