<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.cc

## Purpose
Implements `XrdCryptosslX509Req`, the OpenSSL-backed certificate signing request wrapper. It imports requests from serialized buckets or existing `X509_REQ *`, exposes subject and subject hashes, looks up requested extensions, serializes requests, and verifies request signatures.

## Important APIs, types, and functions
- Bucket constructor reads PEM request content from an `XrdSutBucket` via memory BIO.
- Raw constructor adopts an `X509_REQ *`.
- Destructor frees the request and key wrapper.
- `Subject()` formats and caches request subject.
- `SubjectHash()` returns default or old OpenSSL hash of the subject name.
- `GetExtension()` searches CSR extensions by OpenSSL short name or OID text.
- `Export()` serializes the request into a `kXRS_x509_req` bucket.
- `Verify()` calls `X509_REQ_verify()` with the CSR public key.

## Control flow
Both constructors initialize empty caches, validate input, set `creq`, compute subject, extract the public key with `X509_REQ_get_pubkey`, and wrap it in a public-only `XrdCryptosslRSA`. Extension lookup gets the CSR extension stack, selects NID or text matching mode, and scans until a match. Export writes the request PEM to a memory BIO, copies it into a cached bucket, and returns it. Verification obtains the request public key and checks the CSR signature.

## State and persistence behavior
The object owns `X509_REQ *creq`, cached subject/hash strings, optional cached export bucket, and public key wrapper `pki`. No direct file persistence exists. `Export()` caches the bucket for repeated calls; destructor frees `creq` and `pki` but does not visibly free `bucket`.

## Dependencies and integration points
Depends on OpenSSL X509_REQ/BIO/PEM/X509v3 APIs, `XrdCryptosslRSA`, `XrdCryptosslAux` name formatting, and trace macros. The factory constructs this class from buckets, while proxy creation/signing helpers in `XrdCryptosslgsiAux.cc` create and consume request objects.

## Risks and edge cases
Bucket constructor error paths leak the memory BIO on write/read failures. `GetExtension()` does not free the stack returned by `X509_REQ_get_extensions()`, which OpenSSL expects callers to free. `Verify()` calls `X509_REQ_get_pubkey(creq)` without freeing the returned key. Export error paths can leak BIOs. Cached bucket ownership is ambiguous and likely leaked in the destructor.

## Test signals
Tests should import/export CSR buckets, verify valid and tampered CSR signatures, search extensions by short name and numeric OID, run leak checks around extension lookup and verification, test null/empty bucket behavior, and exercise repeated `Export()` calls for ownership/caching semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.cc -->
