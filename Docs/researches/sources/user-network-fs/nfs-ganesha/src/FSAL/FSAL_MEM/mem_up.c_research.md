# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_up.c

## Purpose
`mem_up.c` implements FSAL_MEM upcall testing. When configured, it starts a looper thread that periodically selects random in-memory objects from each MEM export and sends FSAL upcalls for update, invalidate, and invalidate-close.

## Important APIs, Types, And Functions
The file owns static `mem_up_fridge`. `mem_invalidate()` builds a handle key and calls `up_ops->invalidate(..., FSAL_UP_INVALIDATE_CACHE)`. `mem_invalidate_close()` calls `up_ops->invalidate_close()` similarly. `mem_update()` changes the object ctime/change attributes, prepares an attrlist with `ATTR_CTIME` and `ATTR_CHANGE`, and calls `up_ops->update()`. `mem_rand_obj()` selects an object from an export object list while holding `mfe_exp_lock` for read. `mem_up_run()` is the looper callback. `mem_up_pkginit()` and `mem_up_pkgshutdown()` manage the looper fridge.

## Control Flow
`mem_up_pkginit()` is called from MEM config initialization. If `MEM.up_interval` is zero, no thread is created. Otherwise it initializes a single-thread `fridgethr_flavor_looper` with `thread_delay = MEM.up_interval` and submits `mem_up_run()`. Each run iterates `MEM.mem_exports`, picks up to three random objects per export, and calls update, invalidate, and invalidate-close independently when an object is available. Shutdown sends a stop command with timeout, cancels if needed, destroys the fridge, and clears the global pointer.

## State And Persistence
The upcall worker does not persist data; it mutates in-memory object ctime/change for update tests and sends cache invalidation signals. It relies on the live `MEM.mem_exports` list and each export's `mfe_objs` list. Random selection returns a pointer after dropping the export read lock, so object lifetime is protected only by the broader MEM ref/lifetime behavior.

## Dependencies And Integration Points
The file depends on `mem_int.h`, Ganesha FSAL upcall vectors, fridgethr, op-independent handle-to-key object ops, and the global `MEM` module. It is a test integration with upper cache invalidation paths rather than core filesystem serving behavior.

## Risks
`MEM.mem_exports` is noted in `mem_int.h` as lacking locking for serious use, and `mem_up_run()` iterates it without a module-level lock. `mem_rand_obj()` checks `glist_empty()` before taking `mfe_exp_lock`, then selects and returns an unrefed object pointer after unlocking; concurrent export cleanup could race in stress scenarios. `rand()` is used without explicit synchronization.

## Test Signals
Enable `Up_Test_Interval` and verify update/invalidate/invalidate-close callbacks reach MDCACHE without crashes. Combine with concurrent create/delete/export shutdown under sanitizer. Check that disabling the interval creates no thread and that shutdown handles both normal stop and timeout/cancel paths.
