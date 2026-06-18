<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.hh

## Purpose
Declares the OpenSSL auxiliary API used by the cryptossl factory, certificate implementation, CRL implementation, request implementation, and GSI proxy helper implementation. It is the public bridge between generic XRootD crypto abstractions and OpenSSL-specific utility functions.

## Important APIs, types, and functions
- Declares PBKDF2 hooks `XrdCryptosslKDFunLen()` and `XrdCryptosslKDFun()`, with default length macro `kSslKDFunDefLen`.
- Declares X.509 verification, chain export, chain-to-file, parse-file, parse-bucket, and parse-stack APIs.
- Exposes C-linkage helpers `XrdCryptosslX509ToFile()` and the FILE-based `XrdCryptosslX509ParseFile()` overload for external callers needing C ABI symbols.
- Declares ASN.1-to-UTC and `X509_NAME` formatting helpers.
- Declares proxy certificate helpers such as `XrdCryptosslProxyCertInfo()`, `XrdCryptosslSetPathLenConstraint()`, `XrdCryptosslX509CreateProxy()`, request creation/signing, GSI3 proxy checking, and VOMS attribute extraction.
- Defines tracing bit masks `sslTRACE_*` and proxy manipulation error codes `kErrPX_*`.

## Control flow
This header does not implement control flow, but it defines how `XrdCryptosslFactory` wires function pointers into the generic `XrdCryptoFactory` interface. Most certificate helpers are implemented in `XrdCryptosslAux.cc`; proxy/VOMS helpers declared here are implemented in `XrdCryptosslgsiAux.cc`, which is outside this work item but part of the same module.

## State and persistence behavior
The header declares no persistent objects. Its APIs imply file persistence through certificate chain export and proxy creation functions, and memory persistence through returned `XrdSutBucket`, `XrdCryptoX509Req`, `XrdCryptoX509`, and `XrdCryptoRSA` pointers owned by callers.

## Dependencies and integration points
Includes generic `XrdCryptoAux.hh`, `XrdCryptoFactory.hh`, `XrdCryptoX509Chain.hh`, and OpenSSL `asn1.h`. It forward-declares `XrdTlsPeerCerts` so TLS stack parsing can be exposed without pulling TLS internals into every include. Factory methods in `XrdCryptosslFactory.cc` return pointers to these functions.

## Risks and edge cases
Because this header exposes implementation-specific OpenSSL function signatures, ABI changes or OpenSSL type changes can ripple across the cryptossl plugin. The C-linkage functions require careful signature stability. The proxy helper declarations live here while implementations live in a differently named GSI auxiliary file, so build-system omissions can produce link failures only when those hooks are used.

## Test signals
Compile/link tests should verify every declared factory hook resolves. ABI-facing callers should exercise the FILE overloads. Proxy creation and VOMS tests should include the separate GSI implementation file because this header alone can give a misleading picture of coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.hh -->
