# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.cc

## Purpose

This file implements the XML stats report formatter for OFS counters.

## Important APIs, types, and functions

`XrdOfsStats::Report(char *buff, int blen)` returns the required buffer size when `buff` is null, validates buffer length, snapshots `Data` under `sdMutex`, and formats a `<stats id="ofs">` XML fragment containing role, open counts, handle counts, replies/errors/delays, stage-event counts, and TPC counters.

## Control flow

Callers first may call `Report(nullptr, 0)` to learn a conservative buffer size. With a real buffer, the method fails with `0` if the buffer is too small, otherwise copies counters under lock and uses `sprintf()` with a fixed format.

## State and persistence behavior

The file reads in-memory counters from `XrdOfsStats::Data`. It does not persist state. Snapshotting under the mutex avoids mixed counter values while formatting outside the lock.

## Dependencies and integration points

It depends only on `cstdio` and the stats header. It integrates with XRootD monitoring/status paths that collect OFS statistics.

## Risks and test signals

The conservative `statsz` calculation should be kept large enough for role text and integer growth. XML escaping is not applied to `myRole`; role values should be controlled. Tests should cover size-only calls, too-small buffers, zero counters, non-default role, high counter values, and field ordering expected by monitoring consumers.
