# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.hh

Purpose: declares the stream abstraction used by XRootD configuration and utility code to read/write file descriptors, parse tokenized records, execute helper commands, and capture effective configuration.

Important APIs, types, and functions: public APIs include descriptor management (`Attach`, `AttachIO`, `Close`, `Detach`, `FDNum`, `FENum`), command execution (`Exec`, `Drain`, `isAlive`), parsing (`GetLine`, `GetToken`, `GetWord`, `GetFirstWord`, `GetMyFirstWord`, `GetRest`, `RetToken`), output (`Put`, `PutLine`, `Flush`), error/capture (`LastError`, `Echo`, `noEcho`, `Capture`), and configuration helpers (`SetEnv`, `SetEroute`, `Tabs`, `Wait4Data`).

Control flow: callers typically attach a descriptor or execute a command, then consume records/tokens. Configuration readers use `GetMyFirstWord()` to process local directives and variable assignments while normal stream users can use lower-level token methods.

State and persistence: the class owns descriptors unless detached, owns parser buffers, stores a child PID for executed commands, and references external error and environment objects. Static `theCFG` points to an optional capture string shared across streams.

Dependencies and integration points: forward-declares `XrdOucEnv`, `XrdOucString`, and `XrdOucTList`, includes `XrdSysError`, and depends on POSIX signal/types. It is ABI-sensitive, as shown by reserved fields and the `StreamInfo *myInfo` comment.

Risks and test signals: ownership rules around attached descriptors, child processes, and static capture require careful lifecycle tests. The API exposes mutable internal line buffers that are invalidated by subsequent reads. Tests should cover standalone header use, destructor cleanup, `Detach()` semantics, and capture toggling across multiple streams.
