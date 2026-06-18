# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.cc

Purpose: provides async entry points for `XrdOssCsiFile` by allocating internal AIO wrappers and scheduling staged jobs. It keeps checksum processing off the caller path while preserving range-lock and completion semantics.

Important APIs/functions: `XrdOssCsiFileAioStore::~XrdOssCsiFileAioStore()` deletes cached AIO wrappers. `XrdOssCsiFile::Read(XrdSfsAio*)`, `Write(XrdSfsAio*)`, `pgRead(XrdSfsAio*, opts)`, and `pgWrite(XrdSfsAio*, opts)` allocate `XrdOssCsiFileAio`, initialize it with the parent AIO, operation kind, and checksum options, then schedule the first job. `pgWrite` performs `pgWritePrelockCheck()` before scheduling. `Fsync(XrdSfsAio*)` waits for all active AIOs, performs synchronous `Fsync()`, and completes the callback.

State/control: AIO count is incremented by wrapper initialization and decremented during `Recycle()` in the header-defined class. The store reuses wrappers on a simple freelist.

Dependencies/integration: depends on `XrdScheduler`, `XrdSfsAio`, pages, and the AIO job implementation in the header. Risks include asynchronous object lifetime, completion callback ordering, and prelock validation needing the caller buffer to remain valid. Tests should cover async read/write completion, pg checksum return/verify, close waiting for AIO drain, wrapper reuse, and immediate errors for unopened or readonly files.
