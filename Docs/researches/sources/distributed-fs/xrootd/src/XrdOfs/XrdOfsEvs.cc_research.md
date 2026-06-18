# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.cc

## Purpose

This file implements OFS event sending. It formats filesystem events into text messages, queues them through a bounded message pool, and sends them either to a FIFO/socket target or to an external collector program.

## Important APIs, types, and functions

`XrdOfsEvsFormat::Def()` initializes default message formats, while `Parse()` overrides formats from `notifymsg` text using variables such as `$TID`, `$LFN`, `$CGI`, `$FMODE`, and `$FSIZE`. `XrdOfsEvs::Notify()` formats an enabled event into an `XrdOfsEvsMsg`. `Start()` creates a FIFO target when `Target` begins with `>`, otherwise starts an `XrdOucProg`. `sendEvents()` drains the queue and sends messages through `Feed()` or `XrdOucProg::Feed()`. `getMsg()` and `retMsg()` manage small and large free lists.

## Control flow

The constructor masks enabled events, stores the target, initializes free/queue state, and defines default formats for chmod, close, create, mkdir, mv, open, rm, rmdir, trunc, and fwrite. `Notify()` validates event index, converts mode/size placeholders when needed, obtains a message block, formats text with `snprintf`, appends to the queue, and posts the sender semaphore. The sender thread serializes output so blocked collectors do not stall request threads.

`Start()` chooses output mode. FIFO mode creates an `XRDNET_FIFO` socket and writes with `write()`. Program mode prepares and starts an external program once and feeds event data to it.

## State and persistence behavior

State is runtime-only: enabled event mask, target string, queue pointers, free-list pointers, pool quotas, sender thread ID, FIFO FD, and program object. No event queue is persisted; events can be lost if the process exits or if the bounded message object pool is exhausted.

## Dependencies and integration points

The implementation uses `XrdOucProg`, `XrdOucStream`, `XrdNetSocket`, `XrdSysThread`, POSIX `write/close`, and event data from `XrdOfsEvsInfo`. OFS request paths call `Notify()` after filesystem operations selected by config.

## Risks and test signals

The queue is intentionally bounded; when exhausted, `Notify()` drops events and logs only periodically. `sendEvents()` breaks while holding `qMut` when `endIT` is set and then unlocks afterward, so destructor/thread shutdown paths are delicate. Custom format parsing has fixed buffers and manual variable scanning; tests should cover escaped dollars, brace/bracket variables, too many variables, long formats, and invalid names. Integration tests should validate FIFO and program collector modes, large `mv` messages, queue exhaustion, and disabled event masks.
