# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.hh

Purpose: declares the default BWM scheduling policy and its queue data structures.

Important APIs/types/functions: `XrdBwmPolicy1` overrides `Dispatch`, `Done`, `Schedule`, and `Status`; enum `Flow {In, Out, Xeq, IOX}` indexes internal queues; `refReq` stores reference id and direction; nested `refSch` stores queue head/tail, count, current slots, max slots, and `Add`, `Next`, `Yank`.

Control flow: the header models three queues: incoming queued, outgoing queued, and executing. Slots are consumed from direction queues and represented in Xeq until `Done`.

State and persistence: process-local queue state under `pMutex`, wakeups through `pSem`, and an integer `refID`. No persistent state.

Dependencies and integration points: inherits from `XrdBwmPolicy` and uses XRootD mutex/semaphore wrappers. Constructed from `bwm.policy maxslots`.

Risks: queue helper methods are inline and central to correctness; any linking error affects policy fairness and handle cancellation. No copy/move protections are declared, but policy objects are intended singleton-like.

Test signals: direct unit tests of `refSch::Add/Next/Yank`, policy construction with different slot counts, and concurrent schedule/done behavior.
