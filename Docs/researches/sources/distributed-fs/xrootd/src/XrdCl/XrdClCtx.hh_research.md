# sources/distributed-fs/xrootd/src/XrdCl/XrdClCtx.hh

## Purpose

`XrdCl::Ctx<T>` is a small shared operation-context wrapper. It stores a shared pointer to a raw `T*`, allowing copied pipeline operation objects to share and later update the same underlying context pointer while exposing pointer-like dereference operators.

## Important APIs, types, and functions

Constructors create an empty shared pointer-to-pointer, initialize from `T*`, initialize from `T&`, copy, or move. Assignment from `T*` or `T&` updates the shared stored pointer rather than replacing the shared holder.

`operator*` returns `T&` and `operator->` returns `T*`. Both throw `std::logic_error("XrdCl::Ctx contains no value!")` when the stored pointer is null.

## Control flow

Pipeline APIs accept `Ctx<File>` and similar values by copy/move. Because copies share the same `T**` holder, one stage can update the context pointer and other copies observe the new target. Operation wrappers such as `Checkpoint`, `ChkptWrt`, and other file operations dereference `Ctx<File>` when running.

## State and persistence behavior

The only state is process-local pointer indirection stored in `std::shared_ptr<T*>`. The wrapper does not own the `T` object; it owns only the pointer slot. There is no persistence.

## Dependencies and integration points

Dependencies are `<memory>` and `<stdexcept>`. Integration is with `XrdClFileOperations` and all operation-builder headers that accept `Ctx<File>` or other operation contexts.

## Risks and edge cases

The type name can suggest ownership, but it does not own the context object. Dangling pointers are possible if the referenced object dies while operations still hold `Ctx` copies. The shared pointer-to-pointer design means assignment through one copy mutates all copies, which is intentional but surprising.

Dereferencing an empty context throws at runtime. There is no const-propagation of the pointed object beyond constness of the wrapper. Thread-safety is limited to `shared_ptr` control-block mechanics; concurrent assignment/dereference of the raw pointer slot is not synchronized.

## Test signals

Useful tests would cover empty dereference exceptions, copy-shared assignment behavior, move construction, reference and pointer construction, and operation wrappers observing updated contexts.
