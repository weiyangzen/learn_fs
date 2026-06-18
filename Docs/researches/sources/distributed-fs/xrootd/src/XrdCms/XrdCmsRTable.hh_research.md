# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.hh

Purpose: declares the redirector slot table used for fast replies and state broadcast.

Important APIs/types: `Add`, `Del`, `Find`, `Send`, explicit `Lock` and `UnLock`, private `Rtable[maxRD]`, and `Hwm`. Exports global `XrdCms::RTable`.

Control flow: the explicit lock methods are part of the API because `Find()` must be called while holding the lock and the caller may need to send while the node cannot be deleted.

State and persistence: process-local table initialized to null with high-water mark `-1`.

Dependencies/integration: includes `XrdCmsNode`, `XrdCmsTypes`, and `XrdSysPthread`.

Risks: raw pointer table and external lock discipline are fragile. `maxRD` controls scale and must fit into `short` slot ids used elsewhere.

Test signals: static assertions or compile checks around `maxRD`, and unit tests for table initialization and broadcast selection.
