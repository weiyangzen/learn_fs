# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.cc

## Purpose
`XrdSsiStats.cc` defines the global SSI statistics object and implements XML-like statistics formatting for SSI request/response/resource counters, optionally appended with native filesystem statistics.

## Important APIs and Functions
The file defines `XrdSsi::Stats`. `XrdSsiStats::XrdSsiStats` initializes all counters and filesystem pointer. `XrdSsiStats::Stats(char *, int)` returns either the maximum required buffer size or writes formatted statistics into the provided buffer.

## Control Flow
If `buff` is null, the method formats maximum integer values into a dummy buffer and adds the native filesystem stats size when present. Otherwise it locks `statsMutex`, formats all SSI counters into `buff`, unlocks, then appends `fsP->getStats` output if a filesystem pointer was configured.

## State and Persistence
All counters are in process memory and reset at construction. No statistics are persisted. `setFS` in the header attaches an optional native filesystem stats source.

## Dependencies and Integration Points
It depends on `XrdSfsInterface` and `XrdSsiStats.hh`. `XrdSsiSfs::getStats` calls this method, and other SSI code increments the public counters.

## Risks and Test Signals
There is an apparent formatting typo in `statfmt`: `<mdb>%lld</mdb` lacks a closing `>`. Tests should check XML parsability, buffer-size calculation, appending native stats without overflow, counter values under lock, and behavior when `blen` is smaller than the formatted SSI stats.
