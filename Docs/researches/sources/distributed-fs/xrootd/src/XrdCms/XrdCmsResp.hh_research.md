# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsResp.hh

Purpose: declares asynchronous response callback objects and the message-id response queue.

Important APIs/types: `XrdCmsRespCB` is a semaphore-backed callback used to signal that a `waitresp` was sent. `XrdCmsResp` inherits `XrdOucEICB` and `XrdOucErrInfo`, exposes `Alloc`, `Done`, `ID`, instance/static `Reply`, `Same`, and `setDelay`, and stores callback/buffer state. `XrdCmsRespQ` provides `Add`, `Purge`, and `Rem` over 512 buckets.

Control flow: `XrdCmsResp` acts as both error info and callback object during different phases. `XrdCmsRespCB::Init()` drains stale semaphore posts before reuse.

State and persistence: all state is process-local: ready queue, freelist, response queue buckets, and per-response fields. `RepDelay` is configurable but not used in this `.cc` subset.

Dependencies/integration: includes `XrdOucErrInfo`, pthread wrappers, and CMS protocol headers.

Risks: private inheritance from `XrdOucEICB` in `XrdCmsRespCB` is intentional but unusual. `Same()` always returns 0, so callback matching does not filter. Raw pointers to buffers/callbacks require strict lifecycle control.

Test signals: response queue bucket collision tests, semaphore drain tests, and ABI/compile checks for callback signatures.
