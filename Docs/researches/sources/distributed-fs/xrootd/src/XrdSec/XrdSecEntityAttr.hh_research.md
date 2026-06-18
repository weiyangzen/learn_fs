# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.hh

## Purpose

`XrdSecEntityAttr.hh` declares the mutable extra-attribute API for `XrdSecEntity` and the callback interface for listing key-value attributes.

## Important APIs, Types, And Functions

- `XrdSecEntityAttr` exposes typed-object `Add()`/`Get()`, key-value `Add()`/`Get()`, `Keys()`, and `List()`.
- `XrdSecEntityAttrCB` defines callback actions `Delete`, `Stop`, and `Next`, and pure virtual `Attr(key, val)`.
- Private `entXtra` points to the implementation storage object.

## Control Flow

Authorization and security plugins use this API to attach extra logical identity data even when they receive a const `XrdSecEntity*`. Listing is callback-driven and may request deletion.

## State And Persistence

The API object references entity-owned `XrdSecEntityXtra` state. Attribute state is connection-scoped.

## Dependencies And Integration Points

It uses STL strings/vectors and forward-declares `XrdSecAttr` and `XrdSecEntityXtra`. It is embedded in `XrdSecEntity` as `eaAPI`.

## Risks And Edge Cases

- The callback contract forbids reentrant attribute API calls to avoid deadlock.
- The API is mutable through a pointer on otherwise const entities, so authorization code must coordinate naming and replacement semantics.
- Key names are unconstrained strings; collisions between plugins are possible.

## Test Signals

Compile tests should exercise typed and string attribute APIs from const-entity contexts. Runtime tests should verify callback end marker behavior and replacement rules.
