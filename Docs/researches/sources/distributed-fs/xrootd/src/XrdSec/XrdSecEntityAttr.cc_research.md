# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.cc

## Purpose

`XrdSecEntityAttr.cc` implements thread-safe storage and lookup of typed and key-value attributes attached to an `XrdSecEntity`.

## Important APIs, Types, And Functions

- `Add(XrdSecAttr&)` adds a typed attribute object if no existing object has the same signature.
- `Add(key, val, replace)` adds or optionally replaces a string key-value attribute.
- `Get(sigkey)` returns a typed attribute by signature.
- `Get(key, val)` returns a key-value attribute.
- `Keys()` returns all key-value keys.
- `List(attrCB)` iterates key-values through callback actions `Next`, `Stop`, and `Delete`.

## Control Flow

Every method locks `entXtra->xMutex`. Typed attributes are stored in a vector and compared by signature. Key-values are stored in a map. `List()` calls the callback while holding the mutex, records requested deletions, sends an end marker if iteration was not stopped, and then erases requested keys.

## State And Persistence

The implementation mutates `XrdSecEntityXtra::attrVec` and `attrMap`, both scoped to one entity. No persistent storage exists.

## Dependencies And Integration Points

It depends on `XrdSecAttr`, `XrdSecEntityXtra`, and `XrdSysMutexHelper`. SciTokens uses the key-value API for `request.name` and `token.subject`.

## Risks And Edge Cases

- Callback code must not call `Add()` or `Get()` during `List()` because the mutex is held and the header warns this deadlocks.
- `List()` stores `c_str()` pointers for later deletion; because the map is not modified until after iteration, this is safe but delicate.
- Typed attributes are non-owning until `XrdSecEntityXtra::Reset()` deletes them; callers must allocate accordingly.

## Test Signals

Tests should cover duplicate typed attribute rejection, key add/replace/no-replace, missing gets, key enumeration, callback stop/delete behavior, and concurrent attribute access.
