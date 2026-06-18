# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.cc

Purpose: implements asynchronous response callback handling for redirector responses. It captures original caller error/callback state, queues network replies for decoding, invokes the original callback after `waitresp` synchronization, and pools response objects.

Important APIs/functions: `XrdCmsResp::Alloc()` obtains/reuses a response object and installs a synchronization callback into the caller's `XrdOucErrInfo`; `Recycle()` returns objects to a capped free list; instance `Reply()` queues a decoded network response; static `Reply()` runs the consumer loop; `ReplyXeq()` decodes and invokes the original callback; `XrdCmsRespQ::Add`, `Purge`, and `Rem` manage response lookup by message id.

Control flow: a request that expects delayed callback allocates an `XrdCmsResp`, stores it in a queue, and replaces the original callback with `SyncCB`. When a network reply arrives, `Reply()` enqueues it on the ready queue and posts `isReady`. The reply thread decodes with `XrdCmsParser::Decode()`, waits for `SyncCB` to confirm `waitresp` reached the client, then calls the original callback and arranges for `Done()` to recycle the object.

State and persistence: static ready queue, static object free list capped at 300, per-object response header/buffer/manager name/user id/callback state, and `XrdCmsRespQ` hash buckets. No disk persistence.

Dependencies/integration: depends on `XrdCmsParser`, `XrdOucErrInfo`, `XrdOucBuffer`, SFS return codes, semaphores/mutexes, and client message flow.

Risks: callback lifetime and semaphore ordering are subtle; missing `SyncCB.Post()` can deadlock `ReplyXeq()`. `Alloc()` manually copies selected `XrdOucErrInfo` state and depends on stable path/user storage. `XrdCmsRespQ::Rem()` hashes `msgid % mqSize`; negative ids would be unsafe if ever passed.

Test signals: callback synchronization tests, delayed response decode tests for redirect/wait/data/error, object pool cap tests, purge/rem hash collision tests, and deadlock detection when callback is absent.
