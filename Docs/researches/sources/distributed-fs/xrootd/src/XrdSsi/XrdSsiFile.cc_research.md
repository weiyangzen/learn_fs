# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.cc

Purpose: implements `XrdSsiFile`, the SFS file adapter that either delegates to a real filesystem file for configured paths or exposes an SSI request/response session as file-like operations. This is the entry point translating XRootD file calls into SSI request protocol calls.

Important APIs and control flow: `open()` rejects reuse, optionally delegates to `theFS->newFile()` when `fsChk && FSPath.Find(path)`, otherwise builds an `XrdOucEnv`, allocates `XrdSsiFileSess`, and calls session `open()`. Most methods route to `fsFile` when present and to `fSessP` otherwise: `read()`, `write()`, `truncate()`, `fctl()`, `SendData()`, `setXio()`, and `FName()`. Unsupported SSI operations include `readv()` and `sync()`, while AIO read/write are executed synchronously then completed.

State and persistence: owns either `fsFile` or `fSessP`; destructor deletes the delegated file or recycles the session. It also defines `XrdSsi::EmsgPool`, used elsewhere for error-message buffers. No disk persistence is introduced except through delegated filesystem file operations.

Dependencies and integration: depends on SFS interfaces, `XrdOucEnv`, path-list routing, `XrdSsiFileSess`, and SSI utility error formatting. Risks include mode/operation mismatches, synchronous AIO behavior, null `fSessP` assumptions after failed open, and split semantics between passthrough filesystem paths and SSI resources. Test signals should cover both routing branches, open failure cleanup, fctl GETFD behavior enabling `SendData`, sync/readv unsupported returns, and session destruction on file object deletion.
