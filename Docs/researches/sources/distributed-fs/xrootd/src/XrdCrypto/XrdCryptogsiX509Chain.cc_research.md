# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.cc

## Purpose

`XrdCryptogsiX509Chain.cc` implements GSI-specific certificate-chain verification on top of the generic X.509 chain, including sub-CA handling, end-entity certificate requirements, proxy certificate rules, RFC 3820 extension checks, and proxy path-length enforcement.

## Important APIs and Functions

`Verify(EX509ChainErr &, x509ChainVerifyOpt_t *)` overrides generic verification. It requires at least CA plus EEC/subCA, reorders the chain, reads options (`kOptsRfc3820`, `kOptsCheckSubCA`, path length, CRL, verification time), verifies the top CA, verifies any sub-CAs, optionally returns for sub-CA-only validation, verifies a single EEC, rejects multiple EECs, then walks proxy certificates. `SubjectOK()` enforces proxy subject naming: subject must start with issuer or issuer without the trailing proxy CN, must append exactly one `CN=`.

## Control Flow

Proxy verification checks certificate type, subject naming, optional RFC 3820 `ProxyCertInfo` extension via factory hook, path-length constraints, and then generic signature/time/type verification. Path length is decremented across CA/subCA/EEC/proxy traversal and tightened by proxy extension constraints when present.

## State and Persistence Behavior

The subclass reuses protected chain state (`begin`, `size`, `statusCA`, `lastError`) and stores a non-owning `XrdCryptoFactory *cfact` used to query proxy extension hooks. It mutates CA status and last-error text during verification.

## Dependencies and Integration Points

It depends on `XrdCryptoFactory`, proxy OID constants and hook typedefs, `XrdCryptoX509Chain`, CRLs, and trace macros. It is used by GSI authentication/proxy validation paths.

## Risks and Edge Cases

If `kOptsRfc3820` is set and `cfact` or `ProxyCertInfo()` is null, the code can dereference a null function pointer because the compound condition calls `(*(cfact->ProxyCertInfo()))` after only checking `cfact`. Path-depth errors are recorded but not returned immediately before later validation. The proxy loop exits when `plen == 0` even if unprocessed nodes remain, then returns success, so tests should verify over-depth proxies are rejected as intended. Subject parsing uses substring searches for `/CN=` and `CN=` and may accept malformed distinguished names.

## Test Signals

Tests should cover CA+EEC, sub-CA-only mode, multiple EEC rejection, non-proxy after EEC rejection, RFC 3820 extension missing/present, path-length constraints from options and extensions, proxy subject naming variants, CRL revocation, and null factory hook behavior.
