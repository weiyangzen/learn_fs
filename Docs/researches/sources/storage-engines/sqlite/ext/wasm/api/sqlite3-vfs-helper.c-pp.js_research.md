# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-helper.c-pp.js

## Purpose
This file installs `sqlite3.vfs`, a small helper namespace for JavaScript implementations of `sqlite3_vfs` and `sqlite3_io_methods`. It reduces the boilerplate for binding JS methods into SQLite struct fields and registering a VFS with the core library.

## Important APIs, Types, and Functions
`capi.sqlite3_vfs.prototype.registerVfs(asDefault=false)` validates that `this` is a `sqlite3_vfs` struct wrapper, calls `sqlite3_vfs_register()`, verifies `sqlite3_vfs_find(this.$zName)` returns the same pointer, and returns the struct wrapper on success.

`sqlite3.vfs.installVfs(opt)` accepts an object with optional `io` and `vfs` entries. Each entry contains a StructBinder struct wrapper and a map of JS methods. It calls `struct.installMethods(methods, applyArgcCheck)` for each entry. For a `vfs` entry it also fills `$zName` from `name` when needed, arranges that allocated name string for disposal via `addOnDispose()`, and registers the VFS with optional `asDefault`.

## Control Flow
The file adds one synchronous bootstrap initializer. During bootstrap it captures `sqlite3.wasm`, `sqlite3.capi`, and `sqlite3.util.toss3`, creates a null-prototype `sqlite3.vfs` namespace, extends the `sqlite3_vfs` prototype, and defines `installVfs()`.

`installVfs()` loops over `['io','vfs']`, installs methods for each present entry, handles VFS name allocation and registration for the `vfs` entry, tracks whether any work was done, and throws if neither `io` nor `vfs` was provided.

## State and Persistence Behavior
The helper itself stores only the `sqlite3.vfs` namespace and prototype method. Persistent process state changes occur when `registerVfs()` calls into SQLite's VFS registry. If `installVfs()` allocates a C string for a VFS name, that pointer is attached to the struct's disposal list so it lives as long as the struct wrapper.

## Dependencies and Integration Points
This file depends on the bootstrap-created `sqlite3.capi`, `sqlite3.wasm`, `sqlite3.util`, StructBinder-generated struct wrappers, `sqlite3_vfs_register()`, `sqlite3_vfs_find()`, and each struct wrapper's `installMethods()`, `memberSignature()`, and disposal machinery.

It is used by VFS implementations that need to bind JavaScript callbacks to SQLite's C VFS structs. It is a convenience layer over lower-level StructBinder and C API calls; it does not implement file storage itself.

## Risks and Edge Cases
The helper assumes the caller has already populated struct fields other than methods and optional `$zName`. Registering a malformed VFS can still fail inside SQLite or produce broken runtime behavior. The post-registration pointer check catches name/registry mismatches but not semantic bugs in the method implementations.

If callers allocate structs and then dispose them while SQLite may still call the registered VFS, dangling function pointers or freed name strings are possible. `applyArgcCheck` can detect wrong JavaScript callback arity when requested, but disabling it may hide signature drift.

## Test Signals
Tests should register a minimal VFS with explicit `$zName`, register with `name` requiring C-string allocation, verify `asDefault` behavior, ensure `installVfs({})` throws, ensure non-`sqlite3_vfs` receivers for `registerVfs()` throw, verify `sqlite3_vfs_find()` returns the registered pointer, and run method callbacks with and without argument-count checks.
