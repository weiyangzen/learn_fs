# sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.cc

## Purpose

`XrdSendQ.cc` implements a per-link asynchronous send queue. It tries Linux nonblocking socket sends while the link write mutex is held; if a send cannot complete, it copies the remaining bytes into heap messages and uses the global scheduler to flush them with blocking `send()`. The file was read completely.

## Important APIs, Types, and Functions

`XrdSendQ::Send(const char*, int)` and `Send(const iovec*, int, int)` are the primary caller APIs and require `wMutex` to be locked. `SendNB()` overloads perform Linux-only `MSG_DONTWAIT` sends for contiguous and vector data. `QMsg()` appends copied fragments, schedules the queue runner, enforces `qMax`, and emits slow-client warnings based on `qWarn`. `DoIt()` drains queued messages. `Terminate()` handles link shutdown and object deletion. Private helpers `RelMsgs()` and `Scuttle()` free or quarantine queued messages. The local `LinkShutdown` job calls `XrdLink::Shutdown(true)` asynchronously.

## Control Flow

When no queue runner is active, `Send()` first attempts to write directly. A partial or would-block result is copied into an `mBuff` and queued. If a runner is already active, the whole pending message or current iovec tail is copied directly to the queue. `QMsg()` schedules `this` as an `XrdJob` once per active drain. `DoIt()` locks the write mutex, frees deferred deletion messages, pops the FIFO, unlocks around blocking `send()`, and relocks before checking for more work. On send error it scuttles outstanding messages. Termination either marks an active runner to self-delete or frees queues and deletes immediately.

## State and Persistence Behavior

State is per-object and in memory: FIFO `fMsg`/`lMsg`, deferred `delQ`, socket fd snapshot `theFD`, queued count `inQ`, warning threshold `qWmsg`, discard counter, and `active`/`terminate` flags. Static `qWarn`, `qMax`, and `qPerm` are process-wide knobs, though `qPerm` is settable but unused in this implementation. Lifetime is delicate: active queue runners may delete `this` after unlocking.

## Dependencies and Integration Points

It depends on `XrdLink`, global `XrdGlobal::Sched`, global `XrdGlobal::Log`, `XrdSysMutex`, POSIX `send()`, and Linux `MSG_DONTWAIT`/`MSG_MORE`. It is the buffering layer for network link writes when clients are slow.

## Risks and Edge Cases

The queue copies unsent data into a flexible `mBuff` pattern declared with `mData[4]`; allocation sizes must remain conservative. `QMsg()` can discard on `qMax`, returning failure after data may have been partially sent. `SendNB()` checks `retc == EWOULDBLOCK` instead of `errno == EWOULDBLOCK` in two places, which is likely harmless on Linux where `EAGAIN` usually covers it but is still suspicious. `DoIt()` uses blocking send after unlocking, so link closure races rely on fd invalidation and mutex protocol. `Terminate()` can schedule shutdown before deleting the queue, so link reference accounting must stay correct.

## Test Signals

Tests should simulate full socket buffers, partial sends, iovec partial sends, queue threshold warnings, queue max discard behavior, send errors, and termination with and without an active runner. Linux-specific tests should verify `MSG_MORE` behavior and non-Linux fallback behavior.
