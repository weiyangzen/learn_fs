# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.cc

Purpose: implements the fast redirect/locate response queue. It waits for server response masks, piggybacks compatible requests, times out unresolved requests, and sends either direct redirect/location data or wait replies back to redirectors.

Important APIs/functions: global `XrdCms::RRQ`; `Add()` allocates a slot and queues/piggybacks by key; `Del()` marks a slot ready with zero masks; `Init()` builds response templates and starts responder/timeout threads; `Ready()` accumulates masks and moves a slot to ready when enough responses arrive; `Respond()` drains ready slots; `sendLocResp()`, `sendLwtResp()`, and `sendRedResp()` format and send response variants; `TimeOut()` advances a logical clock and expires wait queue slots; `XrdCmsRRQSlot::Alloc()`/`Recycle()` manage slot free lists and piggyback chains.

Control flow: `Add()` queues a pending slot with `Expire=myClock+1`. `Ready()` updates masks and either waits for additional responders (`minR`) or moves to ready. The responder separates locate piggybacks from redirect piggybacks because they require different wire formats. The timeout thread wakes when wait queue transitions from empty and periodically moves expired slots to ready.

State and persistence: fixed `Slot[1024]` pool, separate wait/ready doubly linked lists, global slot free list, shared response buffers, stats counters, timeout slice/delay, and logical `myClock`. State is in-memory and concurrent.

Dependencies/integration: depends on `Cluster.List`, `Cluster.Select`, `XrdCmsNode::do_LocFmt`, `RTable.Find`, network byte order helpers, timers, and CMS protocol response structs.

Risks: slot 0 is reserved/unusable; running out of free slots causes `Add()` to return 0. Shared `hostbuff/databuff` and response templates are used by the single responder thread; additional responder threads would race. Timeout precision is logical and coarse. Piggyback chains rely on correct key/slot validity and `Recycle()` cleanup.

Test signals: stress tests for 1023 concurrent slots, piggyback locate/select combinations, timeout-to-wait behavior, multi-response `minR`, redirector disconnect during `RTable.Find`, and stats consistency.
