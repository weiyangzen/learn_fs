# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsProtocol.hh

Purpose: declares the CMS `XrdProtocol` implementation and its connection state. It is the class used both for accepted CMS links and scheduled outbound manager connections.

Important APIs/types: public `Alloc`, `DoIt`, `Execute`, `Match`, `Process`, `Recycle`, `Ref`, and `Stats`. Private helpers include `Admit`, `Admit_Redirector`, `AddPath`, `ConfigCheck`, `Dispatch`, `Init`, `Login_Failed`, `Pander`, `Reissue`, `Reply_Delay`, `Reply_Error`, `SendPing`, and `Sync`. `Bearing` distinguishes down/lateral/up connection timeout behavior.

Control flow: `Alloc()` pulls from a static freelist and calls `Init()`. `DoIt()` is the job entry for outbound manager pander roles. `Process()` is the accepted-link entry. `Ref()`/`Sync()` coordinate async jobs with link teardown.

State and persistence: static freelist/parser/read-wait plus per-instance link, node, routing, manager, redirector slot, ref count, and flags. No persistent data is stored in the class directly.

Dependencies/integration: includes `XrdProtocol`, `XrdCmsParser`, `XrdCmsTypes`, and pthread wrappers. It forward-declares CMS manager/node/request/routing types to reduce header coupling.

Risks: header declares `Admit_DataServer`, `Admit_Supervisor`, and `Authenticate()` although this `.cc` subset does not define/use them, likely legacy declarations. Manual pooling and raw pointers make initialization completeness important. `maxReqSize` is fixed at 16 KiB.

Test signals: object-pool reuse tests should assert fields reset by `Init()`; ABI/compile tests should catch stale private declarations; dispatch tests should verify `maxReqSize`.
