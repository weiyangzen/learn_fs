# sources/user-network-fs/samba/source4/ntvfs/ntvfs.h

Purpose: defines the core NTVFS ABI: backend operation tables, module stack contexts, per-connection state, request async state, and file handle backend data. It is the contract that all disk, IPC, and print NTVFS modules implement.

Important APIs and types: `enum ntvfs_type` separates disk, IPC, and print shares. `struct ntvfs_ops` is the central vtable with connect/disconnect, path operations, open/search/ioctl/read/write/lock/info/close, transaction, notify, cancel, print, logoff, and exit callbacks. `struct ntvfs_module_context` links modules in a stack. `struct ntvfs_context` stores protocol, client capabilities, share config, event/messaging contexts, addresses, oplock callbacks, and frontend handle callbacks. `struct ntvfs_request` carries session info, SMB PID, per-request async-state stack, and statistics. `struct ntvfs_handle` stores frontend identity plus per-module backend data. `NTVFS_CURRENT_CRITICAL_SIZES` captures ABI-sensitive sizes for module registration.

Control flow: frontends create `ntvfs_request` instances and call interface functions that dispatch to the first module. Stacked modules call `ntvfs_next_*` wrappers to continue down the chain. Async operations use a linked stack of `ntvfs_async_state`; a backend marks `NTVFS_ASYNC_STATE_ASYNC` when it will reply later.

State and persistence: this header defines in-memory state only. Lifetimes are talloc-based, with handles able to carry one backend data record per module owner. Persistent file semantics live in backend implementations.

Dependencies and integration points: includes raw SMB interface unions, share config, generated security/server-id types, notify/security NDR headers, and `ntvfs_proto.h`. The ABI version is intentionally `0`, with size checks used by registration.

Risks: any struct layout or callback signature change can break modules; callback fields are nullable and callers must guard for `NOT_IMPLEMENTED`; async-state stack misuse can corrupt reply routing. Test signals include module registration version checks, stacked module pass-through, handle callback wiring, and async reply paths.
