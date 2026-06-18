# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.cc

## Purpose
Implements a mutex-protected error-code/message accumulator with optional append semantics and errno integration.

## Important APIs, Types, And Functions
Implemented methods are `Get`, `Msg`, `Msgf`, `MsgVA`, `MsgVec`, `SetErrno`, and private `Setup`. `Msg` builds a vector of up to five text fragments with spaces. `Msgf` and `MsgVA` format into a 2048-byte buffer. `SetErrno` stores errno/error code and either system error text or alternate text.

## Control Flow
All state mutations lock `ecMTX`. `Get(..., rst=false)` snapshots without clearing; reset mode moves the string out, clears `eCode`, and erases the internal string. `Append` state is consumed by `Setup`: when `Delim` is non-zero it appends delimiter plus new text, otherwise it replaces the message.

## State And Persistence
State is in-memory `ecMsg`, `eCode`, default message id `msgID`, and pending delimiter `Delim`. `SetErrno` also writes process/thread-visible `errno`. There is no persistence.

## Dependencies And Integration Points
Depends on `XrdOucECMsg.hh` and `XrdSysE2T` for errno-to-text conversion. It integrates with code wanting chainable message construction and compact error propagation.

## Risks And Test Signals
Risks include `vsnprintf` truncation handling, appending only one delimiter per `Append` call, global `errno` side effects, and alternate text beginning with `*` suppressing message replacement. Test signals include concurrent setters/getters, append chaining, long formatted messages, `SetErrno` with default/alternate/suppressed text, and reset versus non-reset `Get`.
