# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSecurity.hh

Purpose: declares static CMS security helper APIs used by login/authentication and configuration code.

Important APIs/types: `Authenticate`, `Configure`, `getVnId`, `getToken`, `Identify`, `setSecFunc`, and `setSystemID`. Private static `DHS` holds the loaded security service, and `chkVnId()` validates virtual node ids.

Control flow: all operations are static, so no instance state is required. The class acts as a namespace with access to private static service state.

State and persistence: static process-wide security service pointer; generated system id strings/environment are handled in the implementation.

Dependencies/integration: includes `XrdSecInterface.hh` and references CMS headers through `XrdCms::CmsRRHdr` in method signatures.

Risks: because `XrdNetAddrInfo` and `XrdCms::CmsRRHdr` are used without local forward declarations/includes in this header, transitive include order matters. Static global security state complicates tests and reload behavior.

Test signals: header self-sufficiency compile test, repeated configure tests, and API smoke tests with security disabled/enabled.
