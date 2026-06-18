# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.cc

Purpose: Implements hostname validation for peer certificates after TLS connection establishment.

Important APIs/types/functions: XrdTlsNotary::Validate(const SSL *, const char *, XrdNetAddrInfo *) is the main API. Static cnOK controls whether Common Name fallback is permitted. The file includes XrdTlsHostcheck.icc and XrdTlsNotaryUtils.icc in anonymous namespaces, providing matches_subject_alternative_name() and matches_common_name().

Control flow: Validate() obtains the peer certificate, requires SSL_get_verify_result() to be X509_V_OK, checks the Subject Alternative Name extension first, and accepts on MatchFound. If SAN exists but does not match and DNS fallback is unavailable, validation fails immediately. If CN fallback is enabled or DNS fallback is available, it tries the common name. Finally, with addrInfo, it compares the requested host to reverse DNS name information.

State/persistence: Only process-global cnOK is kept. Certificates are fetched from the live SSL session and freed after SAN evaluation.

Dependencies/integration: Called by XrdTlsSocket::Connect() when thehost is provided. Depends on OpenSSL SSL/X509 and XrdNetAddrInfo.

Risks: The implementation frees the peer certificate before later calling matches_common_name() in the visible code path, which would be unsafe if the pointer is used after free; this deserves focused review against compiler/include behavior. CN fallback is deprecated but default-enabled. DNS reverse lookup fallback can be controversial for security.

Test signals: Validate SAN match/mismatch/malformed SAN/no SAN, verified vs unverified certs, CN fallback enabled/disabled, DNS fallback success/failure, and memory-safety under sanitizers.
