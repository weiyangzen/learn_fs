# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.hh

Purpose: declares the in-memory session object backing SSI-mode `XrdSsiFile` instances. It owns resource preparation state and the table of active `XrdSsiFileReq` objects.

Important APIs/types: public methods include static `Alloc()`, `AttnInfo()`, request-table finalization wrappers, `close()`, `fctl()`, `open()`, `read()`, `SendData()`, `SetAuthDNS()`, `setXio()`, `truncate()`, and `write()`. `Resource()` exposes the current `XrdSsiFileResource`. The nested `reqItemCB` keeps a table lookup reference alive across async callback completion.

Control flow and state: private `Init()`, `NewRequest()`, `Reset()`, and `writeAdd()` support lifecycle and multi-segment writes. Static free-list members are protected by `arMutex`; instance state includes resource, identity strings, current partial write buffer, open/progress booleans, EOF bit vector, `XrdSsiRRTable<XrdSsiFileReq>`, and two callback holders.

Dependencies and integration: depends on SFS, XIO, SSI request/resource/table classes, and pthread mutexes. It is not copyable and is created/recycled through static methods. Risks include static pool sizing, stale pointer fields after reuse, and callback-held table items delaying finalization. Test signals should inspect reuse reset, callback reference release, and behavior when close/reset races with outstanding requests.
