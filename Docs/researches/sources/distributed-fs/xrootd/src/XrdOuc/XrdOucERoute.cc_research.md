# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.cc

## Purpose
Implements static helpers for formatting errno-style failures and routing them to logs and/or streams.

## Important APIs, Types, And Functions
`Format` builds `"Unable to <action> <object>; <reason>"` plus optional additional context. It uses `XrdSysError::ec2text` and lowercases an initially uppercase reason. `Route` formats into a 2048-byte buffer, calls `XrdSysError::Emsg` and/or `XrdOucStream::Put`, and returns negative errno.

## Control Flow
`Route` is a thin wrapper: format first, route to each non-null destination, then normalize the return value to `-abs(ecode)` or `-1` when the code is zero.

## State And Persistence
No stored state. Side effects are emitted log/stream messages.

## Dependencies And Integration Points
Depends on `XrdOucStream`, `XrdSysError`, `XrdSysPlatform`, and C string/ctype formatting. It is used by configuration or I/O paths that need consistent user-facing failures.

## Risks And Test Signals
Risks are truncation in fixed buffers, incorrect handling if `etxt1` is null, and returning `blen-1` even for very small buffers. Test signals include known errno formatting, optional context formatting, stream/log dual routing, and return-code normalization.
