<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.cc

## Purpose
Implements `XrdCryptosslX509Crl`, the OpenSSL-backed certificate revocation list wrapper. It loads CRLs from files, FILE handles, or CA certificate distribution-point URIs, caches revoked serials, exposes validity/issuer metadata, verifies CRL signatures, checks revocation, writes CRLs to files, and dumps diagnostic information.

## Important APIs, types, and functions
- Constructors call `Init()`, `Init(FILE*)`, or parse a CA certificate's `crlDistributionPoints` extension and call `InitFromURI()`.
- `Init()` opens local CRL files and delegates to FILE-based initialization.
- `InitFromURI()` downloads a CRL with `wget`, detects PEM/DER, optionally runs `openssl crl -inform DER`, loads the resulting PEM, and removes temporary files.
- `ToFile()` writes PEM CRL content.
- `GetFileType()` detects PEM versus DER by scanning the first non-empty line.
- `hasCriticalExtension()` checks for critical CRL extensions.
- `LoadCache()` iterates revoked entries and stores serials in an `XrdSutCache`.
- `LastUpdate()`, `NextUpdate()`, `Issuer()`, and `IssuerHash()` lazily cache metadata.
- `Verify()` checks the CRL signature against a CA certificate key.
- `IsRevoked()` overloads check integer or string serial numbers against the cache and revocation time.
- `Dump()` logs a human-readable CRL summary.

## Control flow
Local load opens the CRL file, reads a PEM `X509_CRL`, stores the source path, computes issuer, and loads the revocation cache. CA-based construction extracts `crlDistributionPoints`, prints it to a BIO, tokenizes for `URI:` entries, and tries each URI until one initializes. URI initialization builds a temp path under `TMPDIR` or `/tmp`, shell-executes `wget`, checks file type, optionally shell-executes OpenSSL conversion for DER, loads the PEM, then unlinks temporary files. Revocation checks warn on expired CRLs, look up the serial tag in the cache, and compare the requested time to the cached revocation time.

## State and persistence behavior
The object owns `X509_CRL *crl`, cached last/next update times, issuer hashes, source file path, CRL URI, count of revoked certificates, and an `XrdSutCache` of serial entries. URI loads persist temporary files briefly in `TMPDIR` or `/tmp` and remove them after load/conversion. `ToFile()` persists PEM content to a caller-owned FILE.

## Dependencies and integration points
Depends on OpenSSL X509_CRL/PEM/BN APIs, `XrdCryptosslAux` for ASN.1 time and name conversion, `XrdCryptosslRSA`, `XrdSutCache`, tracing, shell tools `wget` and `openssl`, and CA certificate extension lookup from `XrdCryptoX509`. The factory constructs CRLs directly from file/URI option or CA certificate.

## Risks and edge cases
`InitFromURI()` builds shell commands by concatenating URI and file paths without quoting, creating command-injection and whitespace/path risks if URI input is untrusted. It relies on external `wget` and `openssl` availability. `LoadCache()` sets `cent->mtime` to the revocation time and then immediately overwrites `cent->mtime = kCE_ok`; this appears to lose revocation time and likely should set `cent->status`, making `IsRevoked()` unreliable. Integer serial lookup uses lowercase `%x`, while `LoadCache()` stores `BN_bn2hex` uppercase strings, causing mismatch. `Verify()` does not free `X509_get_pubkey()` result. `hasCriticalExtension()` assumes `crl` is non-null. Error paths around BIO and malloc allocation are sparse.

## Test signals
Tests should load PEM and DER CRLs, verify against correct/wrong CA certs, exercise CA distribution point URI parsing with safe local fixtures, check temp cleanup, validate critical extension detection, test revoked serial lookup with upper/lowercase and integer/string paths, assert revocation time semantics, run without `wget`/`openssl`, and include command-injection regression tests if URI input can come from certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.cc -->
