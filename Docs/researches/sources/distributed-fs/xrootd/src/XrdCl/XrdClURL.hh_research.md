# sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.hh

## Purpose

This header declares the `XrdCl::URL` value object, the shared representation for parsed client URLs and opaque query parameters.

## Important APIs, Types, and Functions

`ParamsMap` stores query parameters. Public APIs include constructors, validity/classification helpers, component getters/setters, full/obfuscated URL access, host/channel/location/path views, param serialization and mutation, login token lookup, `FromString`, and `Clear`. Private helpers parse host/path and recompute host ID and URL strings.

## Control Flow

Constructors and setters update the internal representation. `FromString` is the full parser. Getters expose both raw components and derived strings needed by channel reuse, TPC, auth, and logging code.

## State and Persistence Behavior

The object stores protocol, user, password, hostname, port, path, params, host ID, and full URL. It is a copyable in-memory value; no persistence or external ownership is involved.

## Dependencies and Integration Points

Only standard map/string headers are included in the header. It is used across XrdCl copy, transport, stream, redirector, and utility APIs.

## Risks and Edge Cases

Because setters recompute immediately, partial construction through multiple setters can briefly produce invalid or surprising `pURL` values. The header exposes password getter and raw URL getter, so logging code must choose `GetObfuscatedURL` when appropriate. `GetChannelId` includes only selected CGI keys, which must stay aligned with authentication/channel-affinity behavior.

## Test Signals

API tests should verify setter recomputation, path-with-filtered-params behavior, channel ID composition, validity rules, secure/TPC classifications, and round-tripping through `FromString` plus `GetURL`.
