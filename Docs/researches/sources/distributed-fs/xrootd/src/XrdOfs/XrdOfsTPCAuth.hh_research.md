# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.hh

## Purpose

`XrdOfsTPCAuth.hh` declares the authorization-grant object used by TPC rendezvous. It derives privately from `XrdOfsTPC` and specializes the base object for grant lookup, pending callback, TTL expiration, and queue membership.

## Important APIs, Types, and Functions

Public methods are `Add(Facts&)`, `Del()`, inline `Expired()`, detailed `Expired(const char*, int)`, static `Get(Facts&, XrdOfsTPCAuth**)`, and static `RunTTL(int)`. Private static `Find()` searches/removes from the global auth queue. Members are `Next` and `expT`; static members are `authMutex` and `authQ`.

## Control Flow

The header defines a two-sided flow: origins construct an object and call `Add()`, while destinations call `Get()` to consume or wait for a matching object. Expiration is driven by `RunTTL()`.

## State and Persistence Behavior

Each object persists in memory until matched, explicitly deleted, or expired. The expiration timestamp is computed from constructor TTL plus current time. Queue and reference state are inherited from `XrdOfsTPC`.

## Dependencies and Integration Points

The header includes `XrdOfsTPC.hh` and `XrdSysPthread.hh`, making it part of the OFS TPC synchronization layer. It is consumed by `XrdOfsTPC.cc` during authorization and by `XrdOfsTPCAuth.cc` for implementation.

## Risks and Edge Cases

Private inheritance means callers normally interact through static methods or base casts in implementation files; accidental API expansion may expose surprising conversion rules. Expiry uses wall-clock `time(0)`, so clock adjustments can extend or shorten grants.

## Test Signals

Compile coverage should check consumers can forward-declare or include it cleanly. Runtime tests should assert that `Expired()` flips at expected times and that delete/reference behavior is correct around matched grants.
