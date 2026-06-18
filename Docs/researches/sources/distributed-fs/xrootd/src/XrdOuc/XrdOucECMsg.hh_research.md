# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.hh

## Purpose
Declares `XrdOucECMsg`, a small synchronized holder for an integer error code and associated text message.

## Important APIs, Types, And Functions
Public API includes `Append`, `Get`, `hasMsg`, `Msg`, `Msgf`, `MsgVA`, `MsgVec`, `Set`, `SetErrno`, assignment operators for code and message text, and the constructor accepting an optional default message id. Private state is protected by mutable `XrdSysMutex`.

## Control Flow
Callers set or format a message, optionally call `Append` before the next message write, and later retrieve code/text with `Get`. Assignment operators update either code or message under lock.

## State And Persistence
Stores only in-memory message state. The `msgID` pointer is not owned and must remain valid if used as the default prefix in `SetErrno`.

## Dependencies And Integration Points
Includes `<cstdarg>`, `<string>`, and `XrdSysPthread.hh`. It is a reusable utility for error-reporting paths that need safe sharing across threads.

## Risks And Test Signals
The copy assignment from another `XrdOucECMsg` locks only the destination, not the source, so concurrent source mutation can race. Other risks are non-owned prefix lifetime and public methods returning copies with possible staleness. Test signals include thread sanitizer coverage and API behavior for assignment, append, and reset retrieval.
