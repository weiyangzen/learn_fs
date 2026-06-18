# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsHostcheck.hh

Purpose: Declares curl-derived hostname wildcard matching used by TLS hostname validation.

Important APIs/types/functions: Defines CURL_HOST_NOMATCH, CURL_HOST_MATCH, and int Curl_cert_hostcheck(const char *match_pattern, const char *hostname).

Control flow: The implementation is in XrdTlsHostcheck.icc, included inside XrdTlsNotary.cc. XrdTlsNotaryUtils.icc can call Curl_cert_hostcheck while validating certificate SAN or CN names.

State/persistence: No state.

Dependencies/integration: This header is a small imported compatibility layer from curl. It avoids depending on libcurl at runtime by embedding the matching helper.

Risks: Hostname wildcard matching is security-sensitive and must match certificate validation rules. Any behavior change here can allow overbroad certificate matches or reject valid wildcard certificates.

Test signals: Unit test exact names, wildcard prefixes, embedded wildcard rejection, case-insensitivity if implemented by the .icc, malformed inputs, and IDN/punycode expectations if supported elsewhere.
