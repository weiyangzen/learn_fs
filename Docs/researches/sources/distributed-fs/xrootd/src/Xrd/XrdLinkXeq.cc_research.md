## sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.cc

Purpose: implements the concrete link executor: protocol dispatch, blocking and nonblocking output, raw and TLS reads/writes, sendfile fast paths, close/recycle semantics, identity updates, and aggregate link statistics.

Important APIs/types/functions: `Reset()` initializes reusable objects; `Close()` tears down send queues, waits for use count serialization, recycles protocols, detaches from polling, unhooks fd table entries, reports TCP monitoring, and closes the fd unless kept. `DoIt()` runs `Protocol->Process()` until scheduler stickiness ends and reenables or closes the link. `Recv`, `RecvAll`, `Send`, `SendIOV`, and `Send(sfVec)` implement raw I/O. `setNB()` creates `XrdSendQ` on Linux. `setTLS()` initializes and accepts TLS. TLS methods wrap `XrdTlsSocket`. `syncStats()` transfers local counters to globals.

Control flow: accepted links start with a loader protocol. Once matched and activated, poll events schedule `DoIt()`. Protocol return codes control whether the link is reenabled, left disabled for `-EINPROGRESS`, or closed. Close paths serialize users, notify terminators, detach from pollers, unhook the fd table, and recycle protocol objects.

State/persistence: per-link counters accumulate in atomics until `syncStats()`. Global counters track active, max, total, bytes, timeouts, stalls, connection time, and sendfile interruptions. TLS state lives in `tlsIO`; optional `sendQ` owns queued writes.

Dependencies/integration: integrates with `XrdLinkCtl`, `XrdPoll`, `XrdScheduler`, `XrdSendQ`, `XrdTcpMonPin`, `XrdTls`, global `tlsCtx`, `devNull`, logging, and protocol plugins.

Risks: lock ordering is delicate across `opMutex`, `rdMutex`, `wrMutex`, and `statsMutex`. `TLS_Send(sfVec)` appears to add each file segment size to `totamt` before the loop and then adds `retc` again, risking overcounted return/stat values. Linux sendfile corking returns early on errors without uncorking because close is expected; reuse assumptions must hold. Deferred close with negative `LinkInfo.FD` must avoid fd reuse races.

Test signals: integration tests should cover protocol return codes, close callback veto, deferred close with queued sends, raw/TLS partial reads, vector limits above `maxIOV`, sendfile on Linux and TLS fallback, stats synchronization, and TCP monitor notification.
