# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.hh

## Purpose

`XrdSecEntity.hh` declares the core identity object returned by XRootD security authentication and consumed by authorization, monitoring, and protocol layers.

## Important APIs, Types, And Functions

- Public identity fields include auth protocol `prot`, extractor `prox`, `name`, `host`, `vorg`, `role`, `grps`, `caps`, `endorsements`, `moninfo`, raw `creds`, `credslen`, `ueid`, `addrInfo`, `tident`, `pident`, uid/gid, and security monitor pointer.
- `eaAPI` exposes mutable extra attributes through `XrdSecEntityAttr`.
- `Display()`, `Reset()`, constructor, and destructor manage diagnostics and initialization.
- Aliases `XrdSecClientName` and `XrdSecServerName` map to `XrdSecEntity`.

## Control Flow

Authentication protocols populate this object for a connection. Authorization plugins generally receive it as const but can still mutate logical request attributes through `eaAPI`. The object persists for the connection lifetime.

## State And Persistence

State is in memory and connection-scoped. The destructor intentionally does not delete public member pointers; protocol owners must free them. Extra attributes are owned by the entity implementation.

## Dependencies And Integration Points

It forward-declares network address, attributes, monitor, and logging classes. It is included by SciTokens, PSS URL code, security protocol implementations, and monitoring.

## Risks And Edge Cases

- Raw public fields make ownership and const-correctness subtle.
- `host` may be a DNS name or IP based on DNR settings; code needing real hostnames should use `addrInfo`.
- Columnar tuple semantics for `vorg`, `role`, and `grps` must be preserved by producers.

## Test Signals

Tests should verify initialization defaults, protocol truncation behavior, attribute API availability, reset semantics, and integration with authorization plugins that write request attributes.
