# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotaryUtils.hh

Purpose: Declares imported helper types and functions for OpenSSL certificate hostname validation.

Important APIs/types/functions: Defines HostnameValidationResult with MatchFound, MatchNotFound, NoSANPresent, MalformedCertificate, and Error. Declares validate_hostname(const char *hostname, const X509 *server_cert).

Control flow: The header describes RFC 6125-style validation: check Subject Alternative Name first, then Common Name if SAN is absent. The .icc implementation is included into XrdTlsNotary.cc and provides lower-level helpers used by Validate().

State/persistence: No state.

Dependencies/integration: Requires X509 to be visible from OpenSSL includes in the including translation unit. Paired with XrdTlsHostcheck.hh for wildcard matching.

Risks: This file is imported code with its own license block; changes should preserve license terms. It is not include-guarded, so it is intended for controlled inclusion rather than broad public inclusion.

Test signals: Validate all enum outcomes through notary-level tests and direct helper tests where possible, especially malformed NUL-containing SAN/CN data.
