# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.hh

Purpose: declares the callback object passed into asynchronous SFS operations so xrootd can send delayed responses after filesystem completion.

Important APIs and types: `XrdXrootdCallBack` inherits `XrdOucEICB`. `Done()` is the callback entry point. `Func()` and `Oper()` expose operation metadata. `Same()` compares callback arguments by link id. `sendError()`, `sendResp()`, and `sendVesp()` format responses. Static `setVals()` installs logger, stats, scheduler, and port dependencies shared by all callbacks.

Control flow and state: each callback object stores only `Opname` and `Opcode`; most execution state is carried in `XrdOucErrInfo` and the static environment initialized at startup. `Done()` schedules asynchronous response work rather than performing all response I/O inline.

Dependencies and integration: includes xrootd protocol definitions, `XrdOucErrInfo`, and pthread support. Used throughout protocol methods that call asynchronous SFS functions.

Risks and test signals: static environment must be set before use. Tests should verify operation names/codes used in tracing, callback-argument matching, and response helper behavior for empty messages and vectored data.
