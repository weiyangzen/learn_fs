# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.cc

Purpose: Implements construction of the local XRootD open URL for HTTP TPC requests.

Important APIs/types/functions: `XrdHttpTpcUtils::prepareOpenURL` consumes `PrepareOpenURLParams`, appends `oss.task=httptpc`, merges `xrd-http-query`, moves `authz=` into `Authorization` when missing, appends configured header-to-CGI mappings, and adds the first alphabetically ordered `Repr-Digest` as `cks.type`/`cks.value`.

Control flow: It starts an opaque query with `?oss.task=httptpc`. If `xrd-http-query` exists, it splits tokens on `&`; `authz=` is stripped from opaque and copied to request headers, while other tokens remain opaque. It then scans request headers case-insensitively for configured header-to-CGI entries and appends matching values. Finally it appends digest information if present and returns `reqResource + opaque`.

State and persistence: Mutates the request header map by adding `Authorization` if an authz opaque token is present and no auth header already exists. No persistent state.

Dependencies and integration points: Uses `XrdOucTUtils`, TPC handler `OSS_TASK_OPAQUE`, and the HTTP extension request model. Its output is passed to SFS `open`.

Risks: Header-to-CGI values are appended without URL encoding here, so callers/configuration must ensure safe values or rely on upstream encoding. Only the first sorted digest is propagated. `authz=` matching is case-sensitive.

Test signals: Queries with and without `authz`, existing Authorization header preservation, multiple opaque tokens, header2cgi case-insensitive matches, digest propagation order, and resources with preexisting query assumptions.
