# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.cc

Purpose: implements a static producer/consumer queue for prepare requests and converts parsed `XrdCmsRRData` into a durable `XrdCmsPrepArgs` job object that owns the request buffer.

Important APIs/functions: constructor steals `Arg.Buff`, copies protocol header and parsed pointers, computes co-location path when stage+coloc options are present, and prepares a two-element iovec. `getRequest()` waits on `PAReady` and dequeues. `Process()` is the worker loop. `Queue()` appends and wakes the worker when idle.

Control flow: prepare request producers call `Queue()`. The single static worker loop either calls `PrepQ.Prepare()` when disk services are enabled or `DoIt()` to perform server selection/forwarding when local disk is unavailable.

State and persistence: static queue state is `First`, `Last`, `isIdle`, `PAQueue`, and `PAReady`. Each object owns `Data` and frees it in the destructor. No disk persistence occurs here.

Dependencies/integration: depends on `XrdCmsConfig`, `XrdCmsPrepare`, `XrdCmsNode::do_SelPrep`, `XrdJob`, and CMS protocol request structures.

Risks: `Next` is not initialized in the constructor before queueing, relying on later assignment discipline. `Process()` has an apparent leak/ownership issue in the `!Config.DiskOK` branch: `getRequest()->DoIt()` calls `DoIt()`, which deletes only when `do_SelPrep()` returns false; otherwise ownership is external and must be verified. `isIdle` is manually maintained and sensitive to missed posts.

Test signals: thread sanitizer queue tests, destructor ownership tests after buffer stealing, stage+coloc parsing cases, and worker behavior with `Config.DiskOK` both true and false.
