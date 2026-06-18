# sources/object-store/daos/src/engine/drpc_handler.c

## Purpose
Implements the dRPC handler registry used by the engine dRPC listener to dispatch incoming `Drpc__Call` messages by module ID.

## Important APIs
- `drpc_hdlr_init()` allocates `registry_table` with `NUM_DRPC_MODULES` slots.
- `drpc_hdlr_fini()` frees the registry.
- `drpc_hdlr_register()` validates initialization, module range, non-NULL handler, and duplicate registration.
- `drpc_hdlr_register_all()` registers a sentinel-terminated handler list and returns the last non-success status while continuing.
- `drpc_hdlr_get_handler()` validates and returns a module handler.
- `drpc_hdlr_unregister()` and `drpc_hdlr_unregister_all()` clear registrations.
- `drpc_hdlr_process_msg()` dispatches a request to its registered handler and sets `UNKNOWN_MODULE` when missing.

## Control flow
The registry is a global array indexed directly by module ID. Registration fails for invalid IDs, NULL handlers, uninitialized table, or already-used slots. Bulk registration/unregistration walks `struct dss_drpc_handler` entries until `handler == NULL`. Dispatch asserts request/response are non-NULL, looks up the handler, sets response status for unknown module, and otherwise calls the module handler.

## State and persistence behavior
State is process-local and volatile. There is no locking in this file, so expected usage is module initialization/teardown rather than concurrent dynamic registration while dispatching.

## Dependencies and integration
Depends on `daos/drpc_modules.h` for module count and `drpc_handler.h` for handler types. `drpc_listener.c` installs `drpc_hdlr_process_msg` as the listener callback, and `drpc_progress.c` eventually invokes that callback in handler ULTs.

## Risks
No synchronization protects `registry_table`. `drpc_hdlr_fini()` does not NULL the pointer after free, so accidental post-fini calls can pass the uninitialized check if memory still appears non-NULL. Bulk registration can partially succeed and leave earlier handlers installed when a later one fails, requiring callers to unregister on error if atomicity is desired.

## Test signals
Existing `drpc_handler_tests.c` should cover init/fini, invalid module IDs, NULL handlers, duplicate registration, missing modules, bulk registration partial failure, unregister behavior, and dispatch status for unknown modules.
