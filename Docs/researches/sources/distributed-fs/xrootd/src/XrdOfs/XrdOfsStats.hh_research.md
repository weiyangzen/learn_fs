# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.hh

## Purpose

This header declares the OFS statistics container and simple synchronized counter operations.

## Important APIs, types, and functions

`StatsData` contains counters for read/write/POSC opens, unpersisted POSC entries, handles, redirects, started operations, replies, errors, delays, stage event success/error counts, and third-party-copy grants/denials/errors/expirations. `Add()` and `Dec()` increment/decrement counters under `sdMutex`. `Report()` formats counters, and `setRole()` sets the role string reported in XML.

## Control flow

OFS operation paths update individual counters through `Add()`/`Dec()`. Monitoring code calls `Report()` to obtain a snapshot. Configuration or role setup calls `setRole()`.

## State and persistence behavior

All state is in-memory and protected by a single mutex for updates and snapshots. The constructor zeroes `Data` and defaults role to `"?"`.

## Dependencies and integration points

It depends on XRootD pthread wrappers and is referenced by event receiver, handle tracking, request handling, and stats/status reporting code.

## Risks and test signals

Because counters are plain `int`, extreme long-running servers can overflow. `setRole()` stores a raw pointer without copying, so the caller must pass stable storage. Tests should cover synchronized updates, decrement behavior, report snapshots during updates, and role pointer lifetime assumptions.
