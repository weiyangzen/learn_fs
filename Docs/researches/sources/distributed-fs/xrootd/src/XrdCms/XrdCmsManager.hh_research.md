# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.hh

Purpose: declares the single-instance-style manager controller that tracks outbound manager nodes and broadcasts CMS events to them.

Important APIs/types/functions: public `myMans`, `ManTree`, `MTMax`, `Add()`, `Delete()`, `Finished()`, four `Inform()` overloads, `Present()`, `Remove()`, `Rerun()`, `Reset()`, `Start()`, `Verify()`, constructor, and private `Run()`. Static table fields hold active manager nodes.

Control flow: the public API supports manager startup, node admission/removal, topology reconfiguration, reset propagation, and message broadcast.

State and persistence behavior: static active-manager table and per-site current/pending manager lists live for daemon lifetime. No disk persistence.

Dependencies: `YProtocol.hh`, `XrdCmsManList`, `XrdCmsTypes`, pthread mutexes, and forward-declared link/node/list/tree types.

Integration points: central dependency for node command handling, protocol connection jobs, manager tree construction, and cluster event propagation.

Risks: public raw pointers expose owned helper objects. Static shared state means multiple `XrdCmsManager` instances are coordinated manually by site id. Destructor intentionally does not free resources.

Test signals: API compile tests, static table bounds, `Present()` behavior, and integration tests with `XrdCmsProtocol` manager connections.
