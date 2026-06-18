# sources/storage-engines/wiredtiger/src/support/lock_ext.c

## Purpose
`lock_ext.c` exposes WiredTiger spin locks through the extension API. It lets extension code allocate, lock, unlock, and destroy a `WT_EXTENSION_SPINLOCK` while reusing core WiredTiger spin-lock implementation and memory ownership.

## Important APIs, Types, and Functions
`__wt_ext_spin_init` allocates a `WT_SPINLOCK` using the connection default session, initializes it with `__wt_spin_init`, and stores it in `ext_spinlock->spinlock`. `__wt_ext_spin_lock` and `__wt_ext_spin_unlock` cast the opaque extension pointer back to `WT_SPINLOCK` and operate with the caller's session. `__wt_ext_spin_destroy` destroys and frees the allocated lock and nulls the extension handle.

## Control Flow
Initialization clears the opaque pointer, obtains `default_session` from `wt_api->conn`, allocates the lock, initializes it, and unwinds allocation on initialization failure. Lock and unlock are direct wrappers. Destroy uses the default session to match initialization context, then frees the lock.

## State and Persistence Behavior
The only state is the heap-allocated spin lock referenced by `WT_EXTENSION_SPINLOCK.spinlock`. It is process memory owned by the extension lock handle. There is no persistence.

## Dependencies and Integration Points
The file bridges public extension API types (`WT_EXTENSION_API`, `WT_EXTENSION_SPINLOCK`, `WT_SESSION`) to internal connection/session and `WT_SPINLOCK` types. It depends on WiredTiger allocation and spin-lock primitives and is part of the API surface used by loadable extensions.

## Risks
Callers must destroy only initialized locks and must not lock after destroy. The wrappers do not null-check `ext_spinlock->spinlock` in lock/unlock paths. Destroy uses the connection default session, so the API connection must remain valid for the lock lifetime. Extension code must avoid recursive or mismatched lock usage according to the underlying spin-lock semantics.

## Test Signals
Extension API tests should initialize and destroy locks, handle allocation or spin-init failures, lock/unlock from extension sessions, verify the pointer is nulled after destroy, and run concurrent extension threads through the wrapper. Negative tests should document behavior for uninitialized or double-destroy cases if the public API promises anything there.
