# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.cc

## Purpose
`XrdSsiScale.cc` implements the lightweight channel allocator used by SSI client-side session handling to spread requests across endpoint user/channel identifiers and optionally grow that spread under load.

## Important APIs and Functions
`getEnt()` returns an available channel entry or `-1` when all entries are saturated. `retEnt(int)` releases a previously allocated entry. `rsvEnt(int)` reserves a specific existing entry for reusable sessions. `setSpread(short)` configures a fixed spread or, when negative, enables auto-tuning. Private helpers `Tune` and `Retune` manage expansion and the transition from newly added channels back into the full round-robin set.

## Control Flow
`getEnt` scans from `nowEnt` to the current spread, increments the first `pendCnt` below `maxPend`, and classifies the request as active in the original partition or re-active in a newly tuned partition. If a full scan fails and auto-tune is enabled, `Tune` expands the spread and retries. `retEnt` decrements a pending count and triggers `Retune` once the original partition has drained enough relative to the new partition.

## State and Persistence
All state is in memory under `entMutex`: pending counts per entry, active counts, current/beginning scan positions, spread size, and auto-tune flags. There is no persistence. The global `XrdSsi::sidScale` in `XrdSsiServReal.cc` is the process-wide allocator.

## Dependencies and Integration Points
The implementation uses `XrdSysMutex` and `XrdSysError` logging. `XrdSsiServReal` obtains new entries with `getEnt`, `XrdSsiSessReal` reserves/releases entries for reusable tasks, and endpoint URLs embed the user entry when non-zero.

## Risks and Test Signals
Risks concentrate around unsigned counter boundaries, `maxPend` saturation, and partition retuning under concurrent release. Tests should cover fixed spread, negative auto-spread, saturation returning `-1`, reserve/release on invalid entries, retune logging, expansion caps at `maxSprd`, and heavy concurrent `getEnt`/`retEnt` cycles that leave all pending counts balanced.
