# sources/user-network-fs/samba/source4/ntvfs/ntvfs_util.c

Purpose: implements common helpers for request creation, async-state stacking, and NTVFS handle backend-data management.

Important APIs and functions: `ntvfs_request_create` allocates and initializes a request plus its first async state. `ntvfs_async_state_push` and `ntvfs_async_state_pop` let mapping/filter layers wrap backend async replies. `ntvfs_handle_new`, `ntvfs_handle_set_backend_data`, `ntvfs_handle_get_backend_data`, `ntvfs_handle_remove_backend_data`, `ntvfs_handle_search_by_wire_key`, and `ntvfs_set_handle_callbacks` abstract frontend handle allocation/lookup/destruction.

Control flow: request creation copies context, session, SMB PID, client capabilities, statistics time, frontend private data, send function, and initial state. Async push clones the current state flags, stores layer private data and send callback, and links it at the head. Pop removes the current state, propagates its state/status to the next layer, and frees it. Backend-data setters either replace an existing owner record or allocate a new one; the first backend-data insertion calls the frontend `make_valid` callback.

State and persistence: all state is in-memory and talloc-scoped. Handle backend-data records are owned by the handle and tagged with the module owner. Removing the last backend-data record calls the frontend destroy callback.

Dependencies and integration points: relies on callbacks installed in `ntvfs_context.handles`, dlink list helpers, and the async semantics defined in `ntvfs.h`. IPC and POSIX modules use these helpers to bind backend objects to protocol handles.

Risks: `ntvfs_async_state_pop` assumes a lower async state exists; handle callbacks may be unset and must return `NOT_IMPLEMENTED`/NULL; replacing backend data steals ownership and can alter lifetimes. Test signals include first backend-data `make_valid`, last removal `destroy`, wire-key lookup, async push/pop status propagation, and missing callback behavior.
