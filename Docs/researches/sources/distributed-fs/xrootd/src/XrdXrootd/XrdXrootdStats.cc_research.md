# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.cc

## Purpose

This file implements xroot protocol statistics formatting and response delivery. It produces the protocol XML stats block and delegates option-driven global stats collection to `XrdStats`.

## Important APIs, types, and functions

The constructor initializes every counter. `Stats(char *buff, int blen, int do_sync)` formats `<stats id="xrootd">...` XML, optionally returning maximum size when `buff` is null. `Stats(XrdXrootdResponse&, const char *opts)` maps option characters to `XRD_STATS_*` flags and streams the global stats response through an inner callback.

## Control flow

Protocol code updates counters directly and may first synchronize per-link counts into `SI`. When queried, `Stats()` locks `statsMutex`, snapshots counters into XML, unlocks, then appends filesystem stats if configured. The response overload returns simple OK when no option flags are requested, otherwise asks `XrdStats` to call back with buffers or iovecs and sends them through `XrdXrootdResponse`.

## State and persistence behavior

Stats are in-memory counters only. Filesystem stats are pulled live from `fsP`; global server stats are pulled from `xstats`. No counters are persisted across process restart.

## Dependencies and integration points

It depends on `XrdStats`, `XrdSfsFileSystem`, and `XrdXrootdResponse`. It integrates with protocol `Stats()`, query handlers, monitoring, and filesystem stats providers.

## Risks and edge cases

Counter updates outside `statsMutex` can be approximate; some fields are accumulated per-link before sync. XML is produced with `snprintf`; callers must respect the size query path. JSON stats are explicitly not enabled for `J` in this parser.

## Test signals

Tests should verify counter initialization, XML content and size-query behavior, filesystem stats appending, option-to-flag mapping, callback response paths for buffer and iovec, and no-option OK behavior.
