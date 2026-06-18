# sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback.go

## Purpose
Provides the delayed writeback scheduler used by VFS cache items. It queues dirty files, uploads them after `--vfs-write-back`, retries failures with backoff, and allows updates, cancellations, renames, stats, queue inspection, and manual expiry changes.

## APIs, Flow, And State
Public APIs are `New`, `SetID`, `Add`, `Remove`, `Rename`, `Stats`, `Queue`, and `SetExpiry`. `WriteBack` holds a mutex, atomic handle counter, heap of not-yet-uploading `writeBackItem`s, lookup map for queued or uploading items, timer state, and upload count. `Add` either creates an item or updates an existing one; if an upload is active and the file was modified, it cancels and requeues. `processItems` pops expired heap entries until the global transfer limit is reached, starts uploads with cancelable contexts, and stops the timer when the transfer cap blocks progress. `upload` calls the item-supplied `PutFn`, removes successful entries, or requeues failures with exponential delay capped at five minutes. `Rename` cancels active upload, removes duplicate-name queue entries, updates the name, and defers retry.

## Dependencies And Integration
Uses `container/heap`, timers, context cancellation, `fs.GetConfig(...).Transfers`, and `vfscommon.Options.WriteBack`. `vfscache.Item` stores the handle and supplies the `PutFn` that copies local cache data to the remote.

## Risks And Test Signals
Risks include heap index corruption, cancellation deadlocks while waiting for upload goroutines, stale duplicate entries after renames, and stopped timers when transfer capacity becomes available later. Tests cover heap ordering, CRUD helpers, timer state, success/failure retry, modified and unmodified update paths, stats/queue output, expiry mutation, transfer limits, renames, duplicate removal, and explicit upload cancellation.
