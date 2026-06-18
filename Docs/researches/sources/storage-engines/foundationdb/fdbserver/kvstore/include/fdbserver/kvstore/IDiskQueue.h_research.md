# sources/storage-engines/foundationdb/fdbserver/kvstore/include/fdbserver/kvstore/IDiskQueue.h

## Purpose
This header bridges kvstore code to the core FoundationDB disk queue interface. It declares the kvstore-facing factory used to open an `IDiskQueue`.

## Important APIs, Types, And Functions
`openDiskQueue(std::string basename, std::string ext, UID dbgid, DiskQueueVersion diskQueueVersion, int64_t fileSizeWarningLimit = -1)` returns a raw `IDiskQueue*`. The actual interface and version enum come from `fdbserver/core/IDiskQueue.h`.

## Control Flow
Callers provide a basename, file extension, debug UID, disk queue version, and optional file-size warning limit. The returned queue is then used by storage/log components for durable append/read queue behavior.

## State And Persistence Behavior
The opened disk queue is persistent local storage, but this header only exposes construction. File naming and warning-limit behavior are delegated to the implementation and core queue layer.

## Dependencies And Integration Points
It depends directly on the core disk queue header and is consumed by kvstore and log-system-backed stores, including `keyValueStoreLogSystem` declarations in `IKeyValueStore.h`.

## Risks And Test Signals
Ownership of the raw pointer must be clear at call sites. Compatibility between `DiskQueueVersion` and existing queue files is a major integration risk. Tests should cover opening new and existing queues, warning-limit tracing, and invalid/corrupt queue files.
