# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.hh

## Purpose

This header declares `XrdXrootdStats`, the protocol-specific counter block and stats responder for xrootd.

## Important APIs, types, and functions

Counters cover matches, errors, redirects, stalls, get/put file, opens, reads, prereads, readv/writev segments, writes, sync, misc operations, async operations, refresh requests, login/auth outcomes, and signature outcomes. Public methods are `setFS()`, `Stats(char*, int, int)`, and `Stats(XrdXrootdResponse&, const char*)`.

## Control flow

Protocol instances update counters during request execution and synchronize per-link counters into the shared stats object. Query paths call `Stats()` to serialize counters or proxy to the global `XrdStats` object.

## State and persistence behavior

All fields are process memory. `statsMutex` is inherited from `XrdOucStats` and protects formatted snapshots and selected aggregate updates.

## Dependencies and integration points

The header depends on `XrdOucStats` and forward-declared filesystem/global stats/response types. It is referenced from protocol, async, callback, configuration, and execution files.

## Risks and edge cases

Public mutable counters are simple and fast but allow unsynchronized updates. Consumers should treat them as operational telemetry rather than exact transactional accounting.

## Test signals

Tests should ensure every counter appears in XML, filesystem stats are optional, and query options exercise global stats integration.
