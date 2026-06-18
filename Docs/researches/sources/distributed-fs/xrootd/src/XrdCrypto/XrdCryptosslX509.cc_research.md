<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.cc

## Purpose
Implements `XrdCryptosslX509`, the OpenSSL-backed X.509 certificate wrapper. It loads certificates from files, buckets, or existing `X509*`, exposes subject/issuer/hash/serial/validity metadata, classifies certificate type, manages public/private key association, serializes certificates, verifies signatures, dumps extensions, and matches DNS SANs for host certificates.

## Important APIs, types, and functions
- Constructors load from certificate/key files, `XrdSutBucket`, or adopted `X509 *`.
- `CertType()` classifies initialized certs as EEC, CA, proxy, unknown, and detects RFC/GSI3/legacy proxy variants.
- `SetPKI()` adopts a consistent private/public `EVP_PKEY` into the certificate's `XrdCryptosslRSA`.
- `NotBefore()` and `NotAfter()` lazily convert OpenSSL validity times.
- `Subject()`, `Issuer()`, `SubjectHash()`, and `IssuerHash()` lazily cache names and default/old hashes.
- `SerialNumber()` and `SerialNumberString()` expose serial in integer and hex string form.
- `GetExtension()` finds an extension by short name or OID text.
- `Export()` serializes the certificate to a `kXRS_x509` bucket.
- `Verify()` verifies this certificate with a reference certificate public key.
- `DumpExtensions()`, `FillUnknownExt()`, and `Asn1PrintInfo()` provide recursive ASN.1 debug dumping.
- `MatchesSAN()` checks DNS subject alternative names against a requested FQDN.

## Control flow
The file constructor validates file presence, opens with `open`/`fdopen`, reads PEM certificate, caches source path, parses subject/issuer/type, then optionally reads a private key file after enforcing that it is regular and not group/world writable beyond allowed `0640`. If no private key is attached, it wraps the certificate public key as a public-only RSA object. Bucket and raw-X509 constructors deserialize/adopt, then follow the same metadata and public-key initialization. Certificate type detection first checks `basicConstraints` for CA, then detects proxy naming where issuer equals subject without final CN, then parses `proxyCertInfo` or calls `XrdCryptosslX509CheckProxy3`, falling back to legacy CN names `proxy` and `limited proxy`. Metadata getters are lazy and cache strings/time values. SAN matching obtains `subjectAltName`, requires an EEC cert, iterates DNS names only, validates IA5 type, length, and absence of embedded NULs, then calls the inherited/shared hostname matcher.

## State and persistence behavior
The object owns `X509 *cert`, optional serialized `XrdSutBucket *bucket`, and `XrdCryptoRSA *pki`. It caches validity times, subject/issuer strings, old and new hashes, source filename, and proxy type. Destructor frees the certificate and key but does not visibly free `bucket`, so repeated `Export()` cache ownership should be reviewed. File constructor reads from disk but does not write. `Export()` creates and caches a bucket from memory BIO contents.

## Dependencies and integration points
Depends on OpenSSL X509/X509v3/BIO/EVP/PEM APIs, `XrdCryptosslRSA`, `XrdCryptosslAux` utilities, GSI proxy checker declared in aux and implemented elsewhere, trace macros, and generic `XrdCryptoX509`. It is constructed by the factory, by chain parsers in `XrdCryptosslAux.cc`, and by TLS peer stack import.

## Risks and edge cases
Private key consistency is checked only by creating an RSA wrapper around the key; it does not compare the private key to the certificate public key in the file constructor, unlike chain parse helper flows. `BitStrength()` calls `X509_get_pubkey(cert)` without freeing the returned `EVP_PKEY`, causing a leak on each call. `MatchesSAN()` returns false without freeing `gens` when the certificate type is not EEC. Several BIO error paths return without freeing BIOs. `SerialNumber()` converts arbitrary-size serials through decimal string to `strtoll`, which can overflow. Proxy type parsing depends on slash-formatted subject strings. `Export()` caches and returns an owned bucket pointer with ambiguous caller ownership.

## Test signals
Tests should load EEC, CA, RFC proxy, GSI3 proxy, and legacy proxy certificates; check private key permission rejection; verify key/cert mismatch behavior; exercise subject/issuer hash old/default values; export/import bucket round trips; SAN matching for exact, wildcard, embedded NUL, overlong, non-DNS, non-EEC, and absent-SAN cases; run leak checks around `BitStrength()`, `MatchesSAN()`, and export error paths; and verify serial overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.cc -->
