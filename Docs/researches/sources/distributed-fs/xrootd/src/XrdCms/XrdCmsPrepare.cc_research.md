# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepare.cc

Purpose: implements the CMS prepare/staging manager. It tracks pending staged files, dispatches add/delete requests to either the built-in FRM proxy or an external prepare scheduler, sends UDP notifications, and periodically scrubs/reset staging state.

Important APIs/functions: global `XrdCms::PrepQ`; `Add()` submits a prepare request and records pending path; `Del()` cancels by request id; `Exists()` and `Gone()` query/update the pending hash; `Prepare()` stages only when a file is not online; `Inform()` sends `avail` notifications; `Reset()` initializes and refreshes FRM/external scheduler state; `setParms()` configures scrub/reset intervals, external command, message substitutions, and name translation; private `isOnline()`, `Scrub()`, and `startIF()` drive health.

Control flow: `Prepare()` uses OSS `Stat()` with resource-only/access-time flags. Offline files are submitted if staging is allowed, online files notify requestors. `Scrub()` alternates between applying `XrdCmsScrubScan` to remove now-online entries and full scheduler reset after `resetcnt` scans. External scheduler protocol writes `+`, `-`, and `?` command lines and reads pending paths.

State and persistence: in-memory `PTable` tracks pending LFNs and `NumFiles`. External persistence belongs to FRM or the prepare program. Administrative state includes `prepif`, `prepMsg`, `Relay`, `PrepFrm`, `prepOK`, scrub counters, and last error timestamp.

Dependencies/integration: depends on `Config.ossFS`, `Config.DiskSS`, `XrdFrcProxy`, `XrdOucStream`, `XrdOucMsubs`, `XrdNetMsg`, `XrdOss`, scheduler `Sched`, and trace/error logging.

Risks: comments note `Reset()` and `startIF()` must be called with `PTMutex`; public `Reset(const...)` calls private `Reset()` without taking `PTMutex`, so initialization-time single-thread assumptions matter. External scheduler command construction depends on valid, non-null prepare fields. `strcpy(baseAP, aPath)` can overflow if `aPath` exceeds 1023 bytes. UDP notify mutates `notify` temporarily by replacing `/` with null and does not restore it, which is acceptable only because the object is soon discarded.

Test signals: fake OSS plus fake prepare stream tests for add/delete/reset/scrub; FRM proxy integration tests; long path/config fuzzing; notification formatting tests for `udp://host/arg`; and lock-order/thread sanitizer checks.
