# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.hh

## Purpose

This header documents and declares the shared redirect-plugin helper. It gives protocol and non-protocol subsystems one thread-safe API for optional redirect rewriting.

## Important APIs, types, and functions

`Outcome` is the tri-state result: `Unchanged`, `Replaced`, or `Error`. `Init()` registers the plugin, logger, and address-cache TTL. `IsActive()` is a cheap plugin-presence check. `Redirect()` invokes either host or URL plugin methods based on `port`. `ParseURL()` is exposed for unit tests. `SetClockForTesting()` is an explicit test-only hook.

## Control flow

Callers initialize once after loading `redirlib`. At redirect time they pass a target, mutable port/options integer, client address, and output strings. The helper normalizes plugin behavior so callers do not duplicate string-contract or DNS-cache logic.

## State and persistence behavior

The header declares only static behavior. Implementation state is process-wide and in-memory; no redirect decisions are persisted.

## Dependencies and integration points

It forward-declares `XrdNetAddrInfo`, `XrdSysError`, and `XrdXrootdRedirPI` to avoid exposing implementation details. It integrates with `XrdXrootdProtocol::fsRedirPI()` and HTTP TPC handling.

## Risks and edge cases

The API uses a mutable `int &port` for two meanings: host-form port and URL-form redirect options. Callers must follow the documented sign convention. The test clock hook is process-global and must never be used by production code.

## Test signals

Header-level tests should pin the public contract: no plugin means unchanged, host form can mutate port, URL form cannot, error messages have the leading `!` stripped, and `ParseURL()` handles the intended grammar.
