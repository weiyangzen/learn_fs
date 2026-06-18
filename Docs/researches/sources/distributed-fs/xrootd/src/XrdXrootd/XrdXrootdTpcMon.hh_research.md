# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.hh

## Purpose

This header declares the TPC monitoring reporter and its event payload. It gives transfer code a compact structure for reporting completed third-party-copy activity.

## Important APIs, types, and functions

`TpcInfo` contains client id, begin/end `timeval`, source/destination URL specs, file size, ending return code, options, stream count, and reserved byte. `isaPush` and `isIPv4` option bits describe transfer direction and IP family. `Init()` resets defaults. `XrdXrootdTpcMon::Report()` emits one event.

## Control flow

Callers construct or reuse `TpcInfo`, call `Init()`, fill transfer fields, and pass it to `Report()`. The reporter uses its configured protocol and gStream sink.

## State and persistence behavior

The reporter stores a borrowed protocol string and a reference to `XrdXrootdGStream`. The destructor is private because instances are intended to live for process/configuration lifetime.

## Dependencies and integration points

It forward-declares logger and gStream types and is configured by xrootd monitoring code. TPC handlers depend on the payload schema.

## Risks and edge cases

`size_t fSize` formatting and downstream JSON consumers must agree on width. Default strings are empty string literals, so callers should not mutate them. The private destructor prevents stack allocation by ordinary callers.

## Test signals

Tests should verify `Init()` defaults, option bit interpretation, reporter construction with a gStream, and schema stability of emitted records.
