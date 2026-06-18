<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock_private.h -->
# sources/user-network-fs/samba/source3/locking/share_mode_lock_private.h

## Purpose
`share_mode_lock_private.h` provides the narrow private escape hatch for code that must access `struct share_mode_data` behind an opaque `struct share_mode_lock`.

## Important APIs, Types, And Functions
The header forward-declares `struct share_mode_lock` and `struct share_mode_data`, and declares `share_mode_lock_access_private_data(struct share_mode_lock *lck, struct share_mode_data **data)`.

## Control Flow
Callers pass an acquired share-mode lock and receive the cached private data pointer. In the current implementation the function asserts that cached data is present and returns `NT_STATUS_OK`; callers use the status to log or panic depending on context.

## State And Persistence
The header itself stores no state. It grants access to mutable in-memory `share_mode_data`, which later persists to `locking.tdb` if marked modified by the caller or helper routines.

## Dependencies And Integration Points
It is included by `share_mode_lock.c` and selected locking code such as `locking.c` that needs delete-on-close tokens, rename path fields, or other `share_mode_data` internals not exposed in the public header.

## Risks And Test Signals
This private API weakens encapsulation, so callers can create persistence bugs by mutating data without setting modified flags. Test signals include delete-on-close and rename paths that access private data, error-path logging when access fails, and full builds that catch accidental exposure or include-order regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock_private.h -->
