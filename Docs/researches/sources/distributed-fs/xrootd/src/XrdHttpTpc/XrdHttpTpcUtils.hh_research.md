# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.hh

Purpose: Declares the HTTP TPC URL preparation utility.

Important APIs/types/functions: `XrdHttpTpcUtils::PrepareOpenURLParams` holds references to the request resource, mutable headers, configured header-to-CGI map, and repr-digest map. Static `prepareOpenURL` returns the XRootD open URL with TPC opaque metadata.

Control flow: Header documents the key behavior: always append `oss.task=httptpc`, fold `xrd-http-query` into opaque parameters, strip `authz` into Authorization, append configured header CGI values, and include digest metadata.

State and persistence: No owned state. The params struct deliberately passes request headers by mutable reference.

Dependencies and integration points: Includes `XrdHttpExtHandler` for request header map types and is used by `TPCHandler::prepareURL`.

Risks: Because the utility mutates headers, callers need to avoid unintended reuse side effects. Reference members require all referenced maps/strings to outlive the params object.

Test signals: Compile and unit-test `prepareOpenURL` with representative request/header maps.
