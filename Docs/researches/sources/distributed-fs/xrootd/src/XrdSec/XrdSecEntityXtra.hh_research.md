# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.hh

## Purpose

`XrdSecEntityXtra.hh` defines the concrete storage backing the `XrdSecEntityAttr` API.

## Important APIs, Types, And Functions

- `XrdSecEntityXtra` inherits `XrdSecEntityAttr` and passes `this` to the base constructor.
- Public fields include mutex `xMutex`, typed attribute vector `attrVec`, and string attribute map `attrMap`.
- `Reset()` clears all stored attributes.
- Destructor calls `Reset()`.

## Control Flow

`XrdSecEntity` allocates `XrdSecEntityXtra` and exposes it through the base API pointer `eaAPI`. API methods lock and mutate this concrete storage.

## State And Persistence

State is per entity and in memory only.

## Dependencies And Integration Points

It includes maps/vectors, `XrdSecEntityAttr.hh`, and XRootD pthread mutex helpers. It is tightly coupled to `XrdSecEntity` construction and destruction.

## Risks And Edge Cases

- Public storage fields are accessible to implementation files but should not be modified by arbitrary consumers.
- Inheritance plus self pointer means object layout/lifetime is subtle; `eaAPI->entXtra` is the owning concrete object.

## Test Signals

Tests should verify base API methods correctly mutate this storage and destructor cleanup is idempotent after explicit `Reset()`.
