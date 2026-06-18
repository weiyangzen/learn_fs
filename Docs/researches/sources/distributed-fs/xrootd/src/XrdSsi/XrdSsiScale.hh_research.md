# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.hh

## Purpose
`XrdSsiScale.hh` declares the SSI channel scaling allocator. It provides a small concurrency-safe object that tracks pending request pressure per channel and exposes the constants that define default spread, hard limits, and auto-tuning thresholds.

## Important APIs and Types
The public surface is `getEnt`, `retEnt`, `rsvEnt`, and `setSpread`. Constants include `defSprd` 4, `maxSprd` 1024, `maxPend` 64000, and tuning thresholds `minTune`, `midTune`, `maxTune`, and `zipTune`. Private fields are protected by `entMutex` and include `Active`, `reActive`, `begEnt`, `nowEnt`, `curSpread`, `autoTune`, `needTune`, and `pendCnt[maxSprd]`.

## Control Flow
The header establishes that callers must treat entries as leased resources: acquire with `getEnt` or `rsvEnt` and return through `retEnt`. `setSpread` can switch from fixed spread to auto-tuned spread and vice versa.

## State and Persistence
State is volatile process memory only. The constructor initializes a four-channel fixed spread with zero pending counts; no state is serialized across restarts.

## Dependencies and Integration Points
The class depends only on C integer/string headers and `XrdSysPthread.hh`. It is used by the client-side SSI service/session implementation to control endpoint stream identifiers embedded in URLs and to enforce maximum pending work per entry.

## Risks and Test Signals
The ABI exposes constants but not internal layout stability. Tests should verify constructor defaults, spread clamping, negative spread enabling auto-tune, reservation failure after `maxPend`, and that `retEnt` ignores invalid or already-empty entries without underflowing counters.
