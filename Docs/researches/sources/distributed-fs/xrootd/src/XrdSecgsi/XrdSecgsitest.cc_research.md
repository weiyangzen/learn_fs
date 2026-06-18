# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsitest.cc

## Purpose
`XrdSecgsitest.cc` is a standalone integration test utility for GSI-related crypto functionality. It exercises user certificate/proxy loading, proxy recreation, CA chain construction and verification, bucket import/export, proxy request signing, CRL handling, and GSI-specific chain verification.

## Important APIs, types, and functions
The program defines global paths for the end-entity certificate, key, proxy, generated proxy chain, and CA directory. `pdots()` and `pline()` format PASS/FAIL output. `printHelp()` documents environment-driven inputs. `main()` is the full test body and uses `XrdCryptoFactory` hooks such as `X509CreateProxy`, `X509ParseFile`, `X509ExportChain`, `X509ParseBucket`, `X509CreateProxyReq`, `X509SignProxyReq`, `X509ChainToFile`, and `X509Crl`.

## Control flow
The CLI accepts `-v`, `-vv`, and help options. It initializes GSI tracing, sets SUT and crypto trace levels, loads the `ssl` crypto factory, and resolves the effective user's home directory. It locates input files using `X509_USER_CERT`, `X509_USER_KEY`, `X509_USER_PROXY`, and `X509_CERT_DIR`, falling back to conventional Grid Security paths.

The test loads the user certificate and proxy, recreates a proxy from the certificate/key, and validates that the proxyCertInfo extension exists. It walks issuer hashes through up to five CA certificates until it finds a self-signed root. It then parses the proxy file into a chain, adds CAs, reorders, verifies, exports to an `XrdSutBucket`, imports the bucket into plain and GSI-specific chains, and verifies both. Later phases verify direct certificate signatures, create and sign a proxy request, write a signed proxy chain to `<proxy>p`, inspect CRL distribution point extensions, load a CRL, verify its signature, and perform sample revocation checks.

## State and persistence behavior
The test reads real user and CA material from the filesystem and may create or overwrite the user proxy via `X509CreateProxy`. It writes an additional signed proxy chain to the proxy filename with a `p` suffix. There is no isolation or fixture management in the file itself, so running it against a live account can mutate credential files.

## Dependencies and integration points
The file depends on XRootD crypto abstractions, GSI chain classes, SUT serialization buckets, OpenSSL X.509 extension types, and the GSI trace header. It is tightly coupled to an OpenSSL-backed crypto factory named `ssl` and to grid-style certificate directory naming by issuer hash.

## Risks and edge cases
This is an environment-sensitive integration test rather than a deterministic unit test. It assumes valid local credentials, readable private keys, CA files named by issuer hash, CRL distribution information, and network or local CRL availability depending on the crypto factory. The CA array is fixed at five entries. Some failure paths print FAILED and continue, while others exit immediately, so automation should treat the process exit code and output together. Because it can recreate and write proxy files, it should be run only in controlled test environments.

## Test signals
A successful run prints PASSED markers through proxy recreation, chain reorder/verify, GSI chain verify/copy, certificate verification, request creation/signing, proxy chain save, and CRL checks. Valuable negative tests include missing user cert/key/proxy, absent CA issuer file, invalid proxy chain, unavailable `ssl` factory, and CA chain verification failure. The file itself is also a smoke test for the XRootD crypto plugin API used by `xrdgsiproxy`.
