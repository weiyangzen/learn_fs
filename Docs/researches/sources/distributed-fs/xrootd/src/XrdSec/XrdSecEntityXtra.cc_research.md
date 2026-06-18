# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.cc

## Purpose

`XrdSecEntityXtra.cc` implements cleanup for the entity extra-attribute storage.

## Important APIs, Types, And Functions

- `XrdSecEntityXtra::Reset()` locks the extra-state mutex, clears the key-value map, calls `Delete()` on every typed attribute object, and clears the vector.

## Control Flow

`Reset()` is called by `XrdSecEntity::Reset()` and by `XrdSecEntityXtra` destructor. It first discards string attributes, then deletes object attributes through their virtual deletion hook.

## State And Persistence

It clears entity-scoped `attrMap` and `attrVec`. No persistence exists.

## Dependencies And Integration Points

It depends on `XrdSecAttr` and `XrdSecEntityXtra.hh`. It is the cleanup path for all users of `XrdSecEntityAttr`.

## Risks And Edge Cases

- `Delete()` runs while holding `xMutex`; custom attribute deletion code must not call back into the same entity attribute API.
- Attribute object ownership transfers to the entity after successful `Add(XrdSecAttr&)`.

## Test Signals

Tests should add typed attributes with observable `Delete()`, call reset/destructor, and assert each object is deleted once and maps/vectors are empty.
