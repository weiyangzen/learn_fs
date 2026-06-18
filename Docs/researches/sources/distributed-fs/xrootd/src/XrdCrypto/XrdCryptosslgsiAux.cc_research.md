## sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslgsiAux.cc

### Purpose
This file implements OpenSSL-backed GSI proxy-certificate helpers for XrdCrypto. It creates RFC 3820 proxy certificates and proxy certificate requests, signs proxy requests, extracts VOMS attributes from certificate extensions, checks ProxyCertInfo extension validity, and exposes small helpers for reading or modifying proxy path-length constraints.

### Important APIs, Types, and Functions
- `XrdCryptosslProxyCertInfo(const void *extdata, int &pathlen, bool *haspolicy)` decodes modern or legacy ProxyCertInfo extensions and returns the optional path-length constraint.
- `XrdCryptosslSetPathLenConstraint(void *extdata, int pathlen)` decodes a ProxyCertInfo extension and updates its in-memory path-length integer when one exists.
- `XrdCryptosslX509CreateProxy(...)` reads an end-entity certificate and private key from PEM files, generates a new RSA key, builds and signs a proxy certificate, pushes proxy and EEC certificates into `XrdCryptogsiX509Chain`, returns an `XrdCryptoRSA`, and optionally writes the GSI proxy PEM bundle.
- `XrdCryptosslX509CreateProxyReq(...)` creates a new proxy request from an existing proxy certificate, preserving relevant extensions and decrementing the proxy path length.
- `XrdCryptosslX509SignProxyReq(...)` validates the request subject, clamps path-depth constraints, signs the request with the issuer proxy key, and returns an `XrdCryptosslX509`.
- `XrdCryptosslX509GetVOMSAttr(...)` and recursive `XrdCryptosslX509FillVOMS(...)` scan ASN.1 extension payloads for VOMS attribute certificate strings.
- `XrdCryptosslX509CheckProxy3(...)` validates that a proxy has a usable RFC 3820 or legacy ProxyCertInfo extension with a policy language.
- OpenSSL ASN.1 macros define `PROXY_CERT_INFO_EXTENSION_OLD` decoding for legacy proxy layout. Local smart-pointer aliases wrap many OpenSSL types in the newer request-signing paths.

### Control Flow
Proxy creation starts with PEM load of the EEC certificate and private key, expiry and RSA-key checks, then RSA key generation for the proxy. The subject is copied from the issuer and extended with a random `CN=<serial>`. The file builds a critical ProxyCertInfo extension, copies issuer extensions except SubjectAltName, warns if KeyUsage is absent, signs the new certificate with the issuer key, wraps OpenSSL objects in XRootD crypto classes, and optionally writes certificate, private key, and EEC certificate to a 0600 PEM file.

Proxy request creation follows the same subject-extension pattern but emits an `X509_REQ` and uses smart pointers for most temporaries. When extending an existing proxy, it reads the current ProxyCertInfo depth and decrements it when setting the new request's constraint.

Signing a proxy request validates that the request subject is issuer-subject plus a final CN component, with compatibility for older request versions. It copies safe extensions from the issuer proxy, rejects SubjectAltName, derives output path depth from issuer and request constraints, constructs a fresh critical ProxyCertInfo extension, sets validity to the issuer's remaining lifetime, and signs with the issuer private key.

VOMS parsing is recursive ASN.1 walking. It looks for the VOMS Attribute Certificate OID and then collects printable octet strings following the matching attribute-capability OID into a comma-separated `XrdOucString`.

### State and Persistence
Persistent outputs are only produced when `XrdCryptosslX509CreateProxy` receives `fnp`; it writes a proxy bundle with restrictive permissions. Otherwise state is in OpenSSL heap objects transferred to `XrdCryptosslX509`, `XrdCryptosslX509Req`, `XrdCryptosslRSA`, or a caller-owned chain. Random serials are drawn from `XrdSutRndm::GetUInt()`. No global mutable state is maintained here beyond OpenSSL initialization side effects and trace logging.

### Dependencies and Integration Points
The file depends heavily on OpenSSL ASN.1, X509, RSA/EVP, PEM, and X509v3 APIs. It integrates with `XrdCryptosslFactory`, which returns function pointers for proxy creation, request creation, signing, proxy checking, and VOMS extraction. `XrdCryptosslX509` uses `XrdCryptosslX509CheckProxy3` to classify proxy certificates. It also uses `XrdCryptogsiX509Chain`, `XrdCryptosslRSA`, `XrdCryptosslX509Req`, `XrdOucString`, and XrdCrypto error codes.

### Risks and Edge Cases
Manual OpenSSL ownership is inconsistent: older `CreateProxy` paths have many early returns after allocations without full cleanup, while later functions use RAII more consistently. Several decoded `PROXY_CERT_INFO_EXTENSION` objects in helper paths are not freed before return. `XrdCryptosslSetPathLenConstraint` mutates the decoded object but does not re-encode it into the original `X509_EXTENSION`, so callers should verify whether changes persist. Subject parsing relies on one-line string format and `rfind("/CN=")`, which can be brittle for unusual names. Random serial generation is only a 32-bit unsigned integer. VOMS ASN.1 parsing treats printable octet strings as attribute text and may miss non-printable or differently encoded attributes. Some `X509_REQ_get_pubkey` and OpenSSL object returns may need explicit ownership review.

### Test Signals
Useful tests are proxy creation from real PEM EEC/key pairs, path-depth decrement behavior across chained proxies, rejection of SubjectAltName in proxy signing, malformed ProxyCertInfo decoding, OpenSSL 1.1 versus 3.x key generation, VOMS extension extraction with multiple attribute values, and leak/error-path checks under ASAN or valgrind.
