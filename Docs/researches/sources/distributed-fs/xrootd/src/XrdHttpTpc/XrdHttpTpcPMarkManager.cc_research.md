# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.cc

Purpose: Implements packet marking management for HTTP TPC sockets so transfer traffic can emit flow metadata when PMark/scitag is configured.

Important APIs/types/functions: `SocketInfo` captures an fd and address as `XrdNetAddr` and `XrdSecEntity`. `PMarkManager::connect` optionally performs a timed socket connect and registers data-transfer sockets. `startTransfer`, `beginPMarks`, `endPmark`, and `isEnabled` control marker lifetime.

Control flow: Before transfer, `connect` either lets libcurl connect normally or connects with `XrdNetUtils::ConnectWithTimeout` when PMark is enabled. After `startTransfer`, newly connected sockets are queued. `beginPMarks` creates a primary handle with `scitag.flow` and a direction-swapped `pmark.appname` (`http-put` for pull, `http-get` for push), then derives additional handles from the first. `endPmark` erases the handle before socket close.

State and persistence: Maintains queued socket infos and active `unique_ptr<XrdNetPMark::Handle>` handles keyed by fd. No durable storage.

Dependencies and integration points: Uses `XrdNetPMark`, `XrdNetUtils`, `XrdNetAddr`, `XrdSecEntity`, `XrdHttpExtReq`, and `TPC::TpcType`. Called from TPC libcurl open/close socket callbacks and transfer loops.

Risks: PMark is enabled only when both `req.pmark` and non-negative scitag exist. If derived handle creation fails, queued sockets remain for retry. Timing of `startTransfer` is important to avoid marking control connections. Socket close must call `endPmark` before `close` to preserve accounting.

Test signals: Transfers with and without scitag, pull and push appname direction, multistream derived handles, failed timed connect, PMark begin failure retry, and close callback cleanup.
