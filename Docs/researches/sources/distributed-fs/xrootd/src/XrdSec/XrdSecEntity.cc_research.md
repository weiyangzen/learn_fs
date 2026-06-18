# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.cc

## Purpose

`XrdSecEntity.cc` implements construction, reset, and diagnostic display for the connection security entity object.

## Important APIs, Types, And Functions

- Constructor allocates `eaAPI` as a new `XrdSecEntityXtra` and calls `Init()`.
- Destructor deletes `eaAPI->entXtra`, which owns key-value and object attributes.
- `Init(spV)` zeroes protocol/extractor arrays, optionally copies the protocol name, and resets all public fields to null/zero.
- `Reset(spV)` reinitializes fields and clears extra attributes.
- `Display(mDest)` logs protocol, identity fields, credential length, unique ID, uid/gid, and all key-value attributes through a local `AttrCB`.

## Control Flow

Security protocol implementations fill public fields after construction. `Reset()` is used to reuse an entity object, clearing attribute state as well as scalar/pointer fields. `Display()` is diagnostic and iterates attributes under the attribute API.

## State And Persistence

The entity stores many public raw pointers but does not free most of them in `Reset()` or destructor; the security protocol object remains responsible for public member ownership. Extra attributes are owned by `XrdSecEntityXtra` and are deleted on reset/destruction.

## Dependencies And Integration Points

It depends on `XrdSecEntityXtra`, `XrdSecEntityAttr`, and `XrdSysError`. It is used across authentication, authorization, monitoring, PSS URL identity, and SciTokens attribute decoration.

## Risks And Edge Cases

- Public pointer ownership is external and easy to misuse; resetting without freeing protocol-owned fields can leak if the owner does not handle them.
- Destructor deletes `eaAPI->entXtra`; because `XrdSecEntityXtra` inherits `XrdSecEntityAttr`, this relies on the self-referential API layout.
- `Display()` logs sensitive fields such as names, groups, credentials length, and attributes; debug use should be controlled.

## Test Signals

Tests should construct with protocol names, reset with/without protocol, add attributes then reset, verify display includes attributes, and run leak checks with derived attributes.
