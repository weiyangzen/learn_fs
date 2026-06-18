# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.hh

Purpose: Declares the HTTP TPC packet marking manager and socket metadata helper.

Important APIs/types/functions: `XrdHttpTpc::PMarkManager`, nested `SocketInfo`, `connect`, `isEnabled`, `startTransfer`, `beginPMarks`, `endPmark`, and private `addFd`. Members include a queue of socket infos, a map of fd-to-handle, `XrdNetPMark*`, request reference, transfer-start flag, and TPC type.

Control flow: Header documents the intended sequence: connect/register sockets, call `startTransfer` before data transfer, call `beginPMarks` after `curl_multi_perform`, and call `endPmark` before socket close.

State and persistence: Per-transfer in-memory queues and handles. No persistent storage.

Dependencies and integration points: Depends on XRootD networking, security, PMark, and HTTP extension request types. It is embedded in `TPCLogRecord`.

Risks: Holds a reference to `XrdHttpExtReq`, so lifetime must not exceed the request. Public API relies on caller sequence for correct marking and accounting.

Test signals: Unit-level sequencing tests with fake PMark, and integration tests through libcurl socket callbacks.
