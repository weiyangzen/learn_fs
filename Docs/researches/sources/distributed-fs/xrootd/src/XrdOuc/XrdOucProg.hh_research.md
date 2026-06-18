<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.hh

Purpose: Declares the program execution helper used to run external commands or in-process command procedures.

APIs and control flow: Public methods include `Setup()`, `Run()` overloads, `RunDone()`, `Start()`, `Feed()` overloads, `getStream()`, and `isLocal()`. Private `Reset()` and `Restart()` manage parsed arguments and persistent process restart.

State and persistence: Stores optional error route, current stream, inline procedure pointer, parsed argument storage, argument count, and error fd. It owns the stream and argument buffer.

Dependencies and integration: Forward-declares `XrdSysError` and `XrdOucStream`; includes POSIX `sys/types.h`. It is a utility layer for command hooks and helpers elsewhere in XRootD.

Risks and test signals: Users must call `Setup()` before `Run()` or `Start()`, and persistent stream users must drain output. Tests should check overload consistency, destructor cleanup, copy avoidance, and behavior when commands produce large or no output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.hh -->
