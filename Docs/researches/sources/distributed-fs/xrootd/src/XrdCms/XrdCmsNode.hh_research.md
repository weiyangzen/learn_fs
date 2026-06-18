# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNode.hh

Purpose: declares `XrdCmsNode`, the core per-connection/per-server state object and CMS request handler surface.

Important APIs/types/functions: public state flags for offline/bad/RW/staging/manager/peer/bound/known/connected/gone, disk/config fields, all `do_*` protocol handlers, lock/ref helpers, identity/network helpers, send wrappers, manager assignment, share/timezone/version/slot setters, `SyncSpace()`, static bad/RW bit constants, and private lifecycle/filesystem/hash helpers.

Control flow: protocol dispatch invokes `do_*` methods. Cluster selection and manager code use lock/ref helpers to move between global and node locks safely. Send wrappers guard against offline links.

State and persistence behavior: node objects hold process-memory cluster membership and selection state. `refCnt` protects lifetime; `NodeMask` identifies the node in server masks. No durable persistence, but state is continuously propagated by CMS messages.

Dependencies: `XrdLink`, `YProtocol.hh`, `XrdCmsTypes`, `XrdCmsRRQ`, `XrdNetIF`, `XrdNetAddr`, pthread primitives, and atomics. Many implementation dependencies are forward-declared.

Integration points: used by cluster, manager, protocol, routing, request queue, prepare, and cache subsystems. The header is one of the main internal contracts for CMS behavior.

Risks: many public mutable fields make invariants easy to violate outside the class. Lock helpers require callers to hold the documented global lock. Raw identity strings are manually owned. The class is not copy-safe and assumes pointer identity.

Test signals: compile/API dispatch coverage, lock/ref transition tests, identity matching tests, send-offline behavior, state flag transition tests, and integration with routing/cluster selection.
