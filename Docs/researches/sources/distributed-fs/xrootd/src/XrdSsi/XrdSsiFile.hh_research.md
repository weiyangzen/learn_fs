# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.hh

Purpose: declares `XrdSsiFile`, the SFS file wrapper used by the SSI filesystem plugin. It preserves the full `XrdSfsFile` interface while hiding whether a request is served by SSI or a passthrough filesystem.

Important APIs/types: overrides open/close, two `fctl()` forms, `FName()`, compression and mmap queries, sync/preread/read/readv/AIO read, `SendData()`, `setXio()`, `stat()`, truncate, write, and AIO write. Constructor initializes the base `XrdSfsFile` with `myEInfo`.

Control flow and state: private fields are `XrdSfsFile *fsFile`, `XrdSsiFileSess *fSessP`, and `XrdOucErrInfo myEInfo`. Exactly one backend should be active after a successful open. The destructor owns cleanup for both backends.

Dependencies and integration: depends on `XrdSfsInterface.hh` and forward-declares `XrdSsiFileSess`. It is instantiated by SSI SFS server code. Risks include every new SFS method needing the same passthrough-vs-SSI routing decision, and maintaining backend exclusivity. Test signals should instantiate via the SFS factory and verify method routing under both backend kinds.
