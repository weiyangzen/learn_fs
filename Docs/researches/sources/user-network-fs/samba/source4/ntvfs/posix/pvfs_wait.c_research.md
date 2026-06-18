# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_wait.c

Purpose: `pvfs_wait.c` provides the asynchronous wait abstraction used when open, rename, unlink, or setpathinfo must pause for share-mode or oplock-break resolution. It bridges imessaging events, tevent timeouts, ntvfs async setup, and SMB cancel behavior.

Important APIs, types, and functions: Public functions are `pvfs_async_setup`, `pvfs_wait_message`, and `pvfs_cancel`. The local state type is `struct pvfs_wait`, holding list links, the PVFS state, handler, private data, message type, messaging/event contexts, request reference, and completion reason. Local helpers are `pvfs_wait_dispatch`, `pvfs_wait_timeout`, and `pvfs_wait_destructor`.

Control flow: `pvfs_wait_message` allocates a wait object, references the request, optionally registers a message callback for a message type, optionally installs a timeout timer, marks the request async, links the wait into `pvfs->wait_list`, and returns a talloc handle. Incoming messages are filtered by private-data pointer payload, set reason to `PVFS_WAIT_EVENT`, and invoke `ntvfs_async_setup` with a temporary request reference. Timeouts similarly set `PVFS_WAIT_TIMEOUT`. `pvfs_async_setup` then runs the caller-provided handler in the correct ntvfs chain context. `pvfs_cancel` scans waits for the request and triggers `PVFS_WAIT_CANCEL`.

State and persistence behavior: All state is transient. Waits are linked in memory and deregister messaging callbacks on talloc destruction. There is no durable storage.

Dependencies and integration points: It depends on tevent, imessaging/IRPC, ntvfs async state, dlinklist, and retry code in open/rename/unlink/setfileinfo. ODB retry setup owns higher-level pending open-db registration.

Risks: Message filtering uses pointer identity in payloads. Cancellation support depends on callers implementing cancel handling; several retry handlers still have TODO comments. Request lifetime relies on talloc references around async callbacks. Forgetting to free wait handles leaks async capacity and message registrations.

Test signals: Cover event completion, timeout completion, cancel completion, deregistration on free, pointer mismatch ignored, no-fd message validation, and integration with open/unlink/rename retry handlers.
