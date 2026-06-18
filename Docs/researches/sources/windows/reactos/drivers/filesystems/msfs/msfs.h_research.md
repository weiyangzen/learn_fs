# File Research: sources/windows/reactos/drivers/filesystems/msfs/msfs.h

This is the private MSFS header. It defines all driver-private structures and dispatch prototypes.

Key structures:
- `MSFS_DEVICE_EXTENSION`: global FCB list and mutex.
- `MSFS_FCB`: mailslot state, name, server CCB, reference count, timeout, max message size, message queue, CCB list, and cancel-safe pending read queue.
- `MSFS_CCB`: per-open context pointing back to the FCB.
- `MSFS_MESSAGE`: queued message with variable-length payload.
- `MSFS_DPC_CTX`: timer/DPC/event context used for pending read timeouts.

The header also wraps mutex operations with `KeLockMutex` and `KeUnlockMutex` macros, declares all dispatch routines, and declares cancel-safe queue callbacks plus the timeout DPC.

Research notes:
- The FCB combines persistent mailslot metadata with synchronization and pending I/O state.
- Message payload uses a trailing one-byte array idiom.
- The design is small and direct, with no separate namespace or security abstraction.
