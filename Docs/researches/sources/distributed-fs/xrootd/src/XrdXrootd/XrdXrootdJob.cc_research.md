# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.cc

Purpose: implements a keyed external-program job scheduler for xrootd administrative or helper operations. It coalesces duplicate jobs, limits concurrent executions, supports synchronous wait and asynchronous wait-response clients, and cancels/prunes abandoned jobs.

Important APIs/types/functions: local class `XrdXrootdJob2Do` represents one queued/running job. Its `DoIt()`, `addClient()`, `delClient()`, `lstClient()`, `verClient()`, `Redrive()`, and `sendResult()` manage execution and client fan-out. Public `XrdXrootdJob` methods are `Schedule()`, `Cancel()`, `List()`, `DoIt()`, `CleanUp()`, and `sendResult()` for completed cached results.

Control flow: `Schedule()` validates the job key, finds an existing job unless `JOB_Unique` is set, attaches the caller as a sync or async client, or allocates a new table slot and schedules it immediately if below `maxJobs`. Async clients receive `kXR_waitresp`; sync/fallback callers receive `kXR_wait`. `XrdXrootdJob2Do::DoIt()` runs `XrdOucProg`, captures a line of output, translates success/failure/cancellation, sends async results, redrives one waiting job if capacity opens, and removes itself when no polling clients remain. The scheduler job periodically marks jobs and removes clients whose links disappeared.

State and persistence behavior: all state is in memory: `JobTable`, per-job argv copies, client link/instance/stream IDs, job status atomics, result line pointer, max/current job counters, and cleanup marks. Persistent effects are the external program’s side effects and protocol responses sent to clients.

Dependencies: `XrdScheduler`, `XrdOucProg`, `XrdOucStream`, `XrdOucTable`, `XrdOucTList`, `XrdLink`, `XrdXrootdResponse`, xrootd protocol types, tracing, and `XProtocol::mapError`.

Integration points: used by xrootd command paths that need long-running helper programs while preserving client protocol semantics. `List()` produces XML-like fragments for administrative inspection.

Risks: lock scope is complex because job threads execute external programs and then re-enter shared tables. `theResult` points to stream-owned data whose lifetime must outlive polling responses. `sendResult()` sends to links captured earlier; link instance validation is only pruned periodically or when client arrays are full. The fixed client limit of 8 forces sync fallback. Redrive logic depends on `numJobs`, `maxJobs`, and `doRedrive` staying consistent under cancellation.

Test signals: duplicate non-unique jobs share one execution; unique jobs do not coalesce; async client result delivery; sync fallback when max clients/table slots exhausted; cancellation before run, during run, and after completion; disconnected client pruning; redrive ordering when `maxJobs` is exceeded; `List()` status XML for active/waiting/done/cancelled jobs.
