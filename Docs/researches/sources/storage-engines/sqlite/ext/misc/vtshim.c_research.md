# Research: sources/storage-engines/sqlite/ext/misc/vtshim.c

## Purpose

`vtshim.c` provides a shim between SQLite's virtual table interface and runtimes with garbage-collected or externally managed module lifetimes. It exposes `sqlite3_create_disposable_module()` and `sqlite3_dispose_module()` so a host can register a module, later mark it disposed, close/disconnect active child objects, and prevent further calls into freed managed code.

The shim wraps a caller-supplied `sqlite3_module`, forwarding calls while the module is active and returning errors or EOF-like values after disposal.

## Important APIs, Types, And Functions

- `sqlite3_create_disposable_module(db, zName, p, pClientData, xDestroy)` copies the child module, builds a wrapper module, registers it with `sqlite3_create_module_v2`, and returns a `vtshim_aux *` handle.
- `sqlite3_dispose_module(void *pX)` closes all active child cursors, disconnects all active child vtabs, marks the module disposed, and invokes the child auxiliary destructor once.
- `vtshim_aux` owns child aux data/destructor, copied child module, database pointer, module name, disposed flag, list of active wrapper vtabs, and the wrapper `sqlite3_module`.
- `vtshim_vtab` tracks the child vtab and list links back to the owning aux plus active cursors.
- `vtshim_cursor` tracks the child cursor and cursor-list links.
- `VTSHIM_COPY_ERRMSG()` copies child `zErrMsg` into the wrapper vtab error message after forwarded failures.
- Wrapper methods from `xCreate` through `xRollbackTo` forward to corresponding child callbacks when present and not disposed.
- `vtshimAuxDestructor()` is registered with SQLite to release copied module state and child aux data after SQLite no longer references the module.

## Control Flow

Module creation allocates aux state, copies the supplied module, stores the caller's aux/destructor, creates a wrapper module with callbacks only where the child module has callbacks, caps wrapper `iVersion` at 2, and registers the wrapper with SQLite. If allocation or registration fails, it attempts to clean up and returns NULL.

`xCreate`/`xConnect` reject calls after disposal, allocate a wrapper vtab, call the child method with child aux data, and link the wrapper into `pAllVtab`. `xOpen` allocates a wrapper cursor, calls child `xOpen`, sets the child cursor's `pVtab` to the child vtab, returns the wrapper cursor, and links it into the vtab cursor list.

Most cursor/table methods check `bDisposed`, forward to the child, and copy errors on non-OK results. `xDisconnect`/`xDestroy` and `xClose` skip child calls after disposal but always unlink and free wrapper objects. `sqlite3_dispose_module` walks all active vtabs/cursors and calls the child close/disconnect methods directly, then flips `bDisposed`, preventing later wrapper calls from re-entering child code.

## State And Persistence Behavior

State is connection-local and heap-allocated. The shim persists as a registered SQLite module until SQLite invokes the `sqlite3_create_module_v2` destructor. Disposal is not transactional and has immediate effects on all active wrapper objects. Active wrapper cursor/vtab allocations remain until SQLite closes/disconnects them, but their child objects are closed/disconnected during disposal and future calls are blocked or treated as EOF.

The child module is copied by value, so the original `sqlite3_module` memory may be reclaimed by the caller after successful registration. Child aux data is owned by the shim after creation and destroyed at disposal or final aux destruction.

## Dependencies And Integration Points

The code depends on SQLite loadable-extension and virtual-table APIs and is compiled out if `SQLITE_OMIT_VIRTUALTABLE` is defined. It integrates with managed bindings or extension systems that need a deterministic unregister/dispose signal without relying on SQLite to stop calling function pointers immediately.

## Risks And Edge Cases

- `sqlite3_dispose_module` calls child `xClose`/`xDisconnect` but does not null child pointers. Later wrapper `xClose`/`xDisconnect` skips child calls due to `bDisposed`, so this is intentional but relies on the disposed flag.
- Disposal walks linked lists while child close/disconnect code could theoretically interact with SQLite and mutate lists; this is a reentrancy risk.
- `vtshimAuxDestructor` asserts `pAllVtab==0`; if SQLite destroys the module while wrappers remain, this assertion indicates lifecycle misuse.
- If `vtshimCopyModule` fails after aux allocation, the child destructor is not invoked in that branch, unlike the first allocation-failure path.
- Wrapper `iVersion` is capped at 2, so newer module callbacks such as `xShadowName` and `xIntegrity` are not forwarded.
- Some methods copy child error messages even when the child callback's boolean return semantics are not SQLite status codes, such as `xEof` and `xFindFunction`.

## Test Signals

Tests should wrap a mock module, verify normal forwarding for create/connect/open/filter/next/column/rowid/update/transaction callbacks, then call `sqlite3_dispose_module` with active cursors and vtabs and assert child close/disconnect/destructor calls occur once. After disposal, new creates/connects should fail with a clear error, scans should return EOF or errors as coded, and later SQLite close/disconnect should not call child methods again.
