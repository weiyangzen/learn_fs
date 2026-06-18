# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.hh

Purpose: declares route flag lookup and node-method dispatch table helpers for CMS protocol request codes.

Important APIs/types: `XrdCmsRouting` flags include invalid, sync, forward, no args, delayable, repliable, and two async queues. `getRoute()` returns flags for a request code. `XrdCmsRouter` maps request codes to display names and `XrdCmsNode` member-function handlers via `getMethod()` and `getName()`. Namespace exports the global router and per-role routing tables.

Control flow: constructors zero arrays and consume sentinel-terminated init arrays. Lookups return invalid/null/`?` for out-of-range or missing codes.

State and persistence: fixed arrays sized by `XrdCms::kYR_MaxReq`; immutable after initialization.

Dependencies/integration: includes `YProtocol.hh` and forward declares `XrdCmsNode`/`XrdCmsRRData`. Used by `XrdCmsProtocol` dispatch and diagnostics.

Risks: constructors do not guard init array request codes against `kYR_MaxReq`, so bad initializer data could write out of bounds. Route flags are bitmasks that can be combined incorrectly without compiler help.

Test signals: initializer bounds tests/static assertions, route table sentinel tests, and request-name coverage checks.
