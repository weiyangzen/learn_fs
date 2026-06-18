# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRouting.cc

Purpose: instantiates CMS routing tables: request-code-to-node-method dispatch plus per-role validation/behavior flags for manager, redirector, response, server, and supervisor connections.

Important APIs/data: `initRouter` maps request names to `XrdCmsNode::do_*` handlers for login, metadata operations, locate/select, prepare, server status, load, ping/pong, space/state/status/update/usage. `initMANrouting`, `initRDRrouting`, `initRSProuting`, `initSRVrouting`, and `initSUProuting` define `isSync`, `Forward`, `noArgs`, `Delayable`, `Repliable`, `AsyncQ0`, and `AsyncQ1` permissions. Globals `Router`, `manVOps`, `rdrVOps`, `rspVOps`, `srvVOps`, and `supVOps` are constructed from these arrays.

Control flow: `XrdCmsProtocol::Dispatch()` uses the active `XrdCmsRouting` to validate each incoming request and decide sync/async/parse behavior. `Execute()` uses `Router` to invoke the node method and checks `Forward`/`Repliable`/`Delayable`.

State and persistence: static process-wide lookup tables; no runtime mutation after construction.

Dependencies/integration: depends on `XrdCmsNode` handler declarations and `XrdCmsRouting.hh`. It is tightly coupled to protocol constants in `YProtocol.hh`.

Risks: missing or mismatched route entries can silently reject valid requests or allow wrong behavior for a role. `kYR_login` has no handler by design. Adding a request code requires updates in parser schemas and every applicable routing table.

Test signals: table completeness tests comparing protocol constants, route flag tests per role, and integration tests ensuring destructive operations are not accepted from meta-manager roles.
