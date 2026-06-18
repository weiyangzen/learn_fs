# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.hh

Purpose: declares the process-wide prepare queue manager object that coordinates staging requests and pending-file bookkeeping.

Important APIs/types: public methods `Add`, `Del`, `Exists`, `Gone`, `DoIt`, `Init`, `Inform`, `isOK`, `Pending`, `Prepare`, `Reset`, and `setParms` cover queue submission, cancellation, status, initialization, and configuration. Private members include `PTMutex`, `PTable`, `prepSched`, `N2N`, `prepMsg`, `Relay`, `PrepFrm`, `prepif`, and scrub counters.

Control flow: as an `XrdJob`, `DoIt()` can be scheduled periodically for scrub work. The public `Prepare()` entry is used by `XrdCmsPrepArgs::Process()`.

State and persistence: `PTable` and counters are in-memory mirrors of pending staged paths. External scheduler or FRM maintains durable staging work outside this class.

Dependencies/integration: includes `XrdJob`, `XrdScheduler`, `XrdCmsPrepArgs`, `XrdOucHash`, `XrdOucStream`, and pthread wrappers. Exports global `XrdCms::PrepQ`.

Risks: destructor intentionally does nothing, so process-lifetime ownership is assumed. Public methods expose char pointers rather than const-correct strings. The class has both external-program and FRM modes, increasing configuration and test matrix complexity.

Test signals: compile coverage for both FRM-enabled and external scheduler paths, pending count invariants, and scheduled scrub behavior over several intervals.
