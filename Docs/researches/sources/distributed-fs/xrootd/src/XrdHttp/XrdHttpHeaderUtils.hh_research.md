## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.hh

Purpose: declares static HTTP header parsing utilities for digest negotiation and safe request framing.

Important APIs/types: `parseReprDigest()` fills a map of digest name to decoded digest value. `parseWantReprDigest()` fills a map of lowercase digest name to preference. `parseContentLength()` returns parsed `ssize_t` or specific negative errors for empty, malformed, or overflow values. `parseTransferEncoding()` returns success only when a non-empty transfer-coding list contains `chunked` as the last token, with specific negative errors for empty, missing, or misplaced chunked.

State and persistence: no class instances or static data are declared; output is entirely caller-owned.

Dependencies and integration: included by HTTP request parsing code. The comments explicitly tie behavior to RFC 9112 and RFC 7230 framing rules, making this a security boundary.

Risks and test signals: keep comments and implementation synchronized because callers may map error codes to HTTP 400 responses. Tests should assert every documented negative code and ensure no valid legacy inputs are accidentally rejected.
