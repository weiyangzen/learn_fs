# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.cc

## Purpose
Implements administrative and notification channels for `cmsd`: primary/proxy/admin login handling, suspension/resume commands, alternate data-server monitoring, event relaying, and forwarding of file availability/removal events to managers.

## Important APIs, Types, and Functions
Local `AdminReq` queues relay requests with static semaphore/mutex state. Thread entry points include `AdminLogin`, `AdminMonAds`, `AdminMonARE`, and `AdminSend`. Public methods implemented include `InitAREvents()`, `Login()`, `MonAds()`, `Notes()`, `Relay()`, `RelayAREvent()`, `Send()`, and `Start()`. Private helpers include `AddEvent()`, `BegAds()`, `CheckVNid()`, `Con2Ads()`, `do_Login()`, `do_Perf()`, `do_RmDid()`, and `do_RmDud()`.

## Control Flow
`Start()` launches the relay thread, optionally begins alternate data-server monitoring, then accepts admin sockets and spawns login handlers. `Login()` requires an initial `login` command and then dispatches text commands such as `resume`, `suspend`, `perf`, `rmdid`, and `newfn`. Primary login sets frontend state and hands the socket to `Relay()`. Notification sockets loop over `gone`, `have`, `stage`, and related events. ARE mode queues events to `RelayAREvent()`, which calls the external stat event function and informs managers.

## State and Persistence Behavior
Static state tracks admin relay queues, ARE queue/list/semaphore, primary-online flag, and optional startup sync semaphore. Instance state stores stream, server type/name, and primary flag. No durable storage is written, but CMS cluster state, prepare queues, and manager notifications are mutated.

## Dependencies and Integration Points
Depends on X/Y protocol headers, CMS config/manager/meter/prepare/state/trace, XrdNet sockets, name translation, semaphores, timers, and OSS stat callback types. Integrates with `XrdCmsManager::Inform`, `CmsState.Update`, `PrepQ`, and `XrdOucName2Name`.

## Risks and Edge Cases
Thread entry passes the address of local `InSock` into a new thread, creating a race if the accept loop overwrites it before the thread reads it. `AdminReq::numinQ` is read without locking in `Send()`. Several loops are intentionally infinite. Login and notification parsing trust command token order. Name translation failures can suppress events. Relay write failure requeues the current item and reconnect behavior depends on primary login.

## Test Signals
Tests should cover login role validation, VNID mismatch handling, suspend/resume state updates, duplicate primary rejection, relay queue overflow, notification command parsing, PFN/LFN translation paths, alternate data-server reconnect, and ARE callback delivery.
