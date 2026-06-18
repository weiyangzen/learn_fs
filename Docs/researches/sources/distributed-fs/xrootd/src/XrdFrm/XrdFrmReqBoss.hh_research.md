## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.hh

Purpose: declares the request-boss abstraction that owns one family of priority request files and a processing thread.

Important APIs/types: public methods `Add()`, `Del()`, `Process()`, `Start()`, and `Wakeup()` provide queue mutation, worker execution, initialization, and semaphore signaling. `Server()` is declared but not implemented in this subset. Private `Register()` handles cluster registration requests. Fields include an `XrdSysSemaphore`, an array of `XrdFrcReqFile *` by priority, the persona name, queue number, and a posted flag.

State and persistence: persistent state is delegated to `XrdFrcReqFile`; the class itself manages runtime thread synchronization and queue identity.

Dependencies and integration: included by `XrdFrmXfrDaemon.hh`; queue numbers are `XrdFrcRequest` queue constants. It is the bridge between external request ingestion and the in-memory transfer queue.

Risks and test signals: the declared `Server()` without a nearby definition should be checked by link coverage. Tests should instantiate multiple bosses to ensure the static wakeup mutex in the implementation does not cause missed signals or unintended serialization.
