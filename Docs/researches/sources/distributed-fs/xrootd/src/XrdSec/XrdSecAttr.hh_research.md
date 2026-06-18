# sources/distributed-fs/xrootd/src/XrdSec/XrdSecAttr.hh

## Purpose

`XrdSecAttr.hh` defines the base class for typed extension objects attached to an `XrdSecEntity`.

## Important APIs, Types, And Functions

- `XrdSecAttr(const void *dSig)` stores a unique signature pointer for the derived attribute type.
- Virtual `Delete()` defaults to `delete this` and can be overridden for custom deletion.
- Destructor is protected, forcing deletion through `Delete()`.
- `XrdSecEntityAttr` is a friend so it can inspect `Signature`.

## Control Flow

Derived classes choose a stable unique signature, instantiate attributes, and add them through `XrdSecEntityAttr::Add(XrdSecAttr&)`. Retrieval uses the same signature pointer and downcasts by convention.

## State And Persistence

Each attribute stores only its signature in the base. Derived objects carry their own state and are deleted when the entity extra state resets or is destroyed.

## Dependencies And Integration Points

It forward-declares `XrdSecEntity` and integrates with `XrdSecEntityAttr` and `XrdSecEntityXtra`.

## Risks And Edge Cases

- Signature uniqueness is a convention, not enforced globally.
- Attribute objects are stored by pointer; callers must not stack-allocate attributes whose lifetime is shorter than the entity.
- Custom `Delete()` implementations must be correct to avoid leaks.

## Test Signals

Tests should add a custom derived attribute, reject duplicate signatures, retrieve it by signature, and verify deletion during entity reset/destruction.
