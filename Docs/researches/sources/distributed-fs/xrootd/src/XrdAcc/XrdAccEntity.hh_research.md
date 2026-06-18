# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.hh

## Purpose

`XrdAccEntity.hh` declares the compiled authorization entity attribute cache used during access checks. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccEntityInfo` carries name, host, virtual org, role, and group for rule matching. `XrdAccEntity` derives from `XrdSecAttr` and exposes static `GetEntity()`, `Next()`, `PutEntity()`, and `setError()`. `XrdAccEntityInit` is an RAII helper that obtains an entity and attaches a new one on destruction.

## Control Flow

`Next(int&, XrdAccEntityInfo&)` is the iterator used by `XrdAccAccess`. It updates VO/role/group while caller-provided name and host remain intact. RAII setup/teardown avoids cache insertion races and leaks.

## State and Persistence Behavior

Objects own duplicated source strings and vector entries pointing into those strings. Cached state is attached to `XrdSecEntity` through `eaAPI` and keyed by a static signature.

## Dependencies and Integration Points

It depends on `XrdSecAttr` and forward declarations for tokenizer, security entity, and error routing. It is tightly integrated with `XrdAccAccess`.

## Risks and Edge Cases

The class has a private destructor and lifecycle is tied to the security attribute API. `Next()` does not reset name/host, which is intentional but requires callers to initialize them before iteration. Invalid compiled entities return null and force fallback access behavior.

## Test Signals

Tests should validate iteration semantics, RAII cache insertion, object reuse, and correct preservation of caller-provided name/host.
