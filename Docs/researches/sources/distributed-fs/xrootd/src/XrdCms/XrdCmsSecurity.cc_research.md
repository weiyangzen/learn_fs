# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.cc

Purpose: implements CMS security handshake helpers, security service loading, virtual node id creation, token retrieval, and system id export.

Important APIs/functions: `Authenticate()` is server-side authentication over CMS `kYR_xauth` request/response loops using `XrdSecService`; `Configure()` loads the security service and protocol factory; `getVnId()` obtains a virtual node id from a file, literal value, or plugin; `getToken()` returns outbound security parameters; `Identify()` is client-side credential exchange; `setSecFunc()` injects a protocol factory; `setSystemID()` builds and exports `XRDCMSVNID`, `XRDCMSCLUSTERID`, and `XRDCMSSYSID`; private `chkVnId()` validates length/characters.

Control flow: authentication loops exchange CMS auth messages until the XrdSec protocol succeeds or fails. `getVnId()` dispatches by leading character: `<` file, `=` literal, `@` plugin. `setSystemID()` derives an instance and cluster id from `XRDINSTANCE`, optional vnid/tag, and manager list suffix differences.

State and persistence: static `DHS` security service and module-level `getProtocol`. Environment variables are exported for CMS system identity. No files are written except reading vnid input.

Dependencies/integration: uses `XrdCmsTalk`, `XrdSecLoadSecurity`, `XrdSecProtocol`, `XrdOucPinLoader`, `XrdOucTList`, `XrdNetAddrInfo`, `XrdLink`, and `XrdSysFD`.

Risks: `chkVnId()` allows most punctuation except `&` and space; security policy depends on that being acceptable. `setSystemID()` returns string-literal error markers cast as `char *` for some failures and heap strings for success, so callers must distinguish ownership. `Configure()` serializes service load with a static mutex but global `DHS` replacement semantics need care. `Authenticate()` sends `Toksz+1`, including null terminator.

Test signals: mock XrdSec handshake success/failure loops, vnid file/literal/plugin validation, invalid characters/length tests, environment export tests, and ownership tests for `setSystemID()` return values.
