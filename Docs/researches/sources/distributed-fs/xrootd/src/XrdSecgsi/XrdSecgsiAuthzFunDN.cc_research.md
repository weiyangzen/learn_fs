# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunDN.cc

## Purpose

`XrdSecgsiAuthzFunDN.cc` implements an example or simple authorization plugin for the GSI protocol. It exports the standard authz plugin symbols expected by `XrdSecProtocolgsi::LoadAuthzFun`: `XrdSecgsiAuthzFun`, `XrdSecgsiAuthzKey`, and `XrdSecgsiAuthzInit`. Its main behavior is minimal: it sets a dummy VO value, and its cache key is derived from the subject DN of the end proxy certificate.

The filename and comments indicate DN-based authorization behavior, but the authorization function itself is effectively a placeholder that always succeeds after setting `entity.vorg`.

## Important APIs and functions

- `XrdVERSIONINFO(XrdSecgsiAuthzFun, secgsiauthz)`, `XrdVERSIONINFO(XrdSecgsiAuthzKey, secgsiauthz)`, and `XrdVERSIONINFO(XrdSecgsiAuthzInit, secgsiauthz)` publish version metadata for dynamic loading.
- `extern XrdOucTrace *gsiTrace` integrates with the main GSI tracing macros.
- Static `gCertfmt` records the credential format requested by the plugin: default `1` for PEM base64, `0` for raw chain pointer.
- `XrdSecgsiAuthzFun(XrdSecEntity &entity)` logs a dummy call, sets `entity.vorg = strdup("VO.dummy.test")`, and returns success.
- `XrdSecgsiAuthzKey(XrdSecEntity &entity, char **key)` validates inputs, reconstructs or uses the proxy chain depending on `gCertfmt`, reorders PEM-parsed chains, selects `chain->End()`, extracts its subject DN, allocates `*key` with `new char[]`, copies the DN, and returns success.
- `XrdSecgsiAuthzInit(const char *cfg)` tokenizes space-separated config and recognizes `certfmt=raw`; it returns the credential format expected by the plugin.

## Control flow

The main protocol loads the plugin, calls `XrdSecgsiAuthzInit`, then invokes `XrdSecgsiAuthzKey` to get a cache key whenever authz should run. If the returned key is not already cached, the protocol calls `XrdSecgsiAuthzFun` and then caches selected `XrdSecEntity` fields.

For PEM credentials, `XrdSecgsiAuthzKey` wraps `entity.creds` in an `XrdOucString`, creates an `XrdSutBucket`, parses it into a new `XrdCryptoX509Chain` via `XrdCryptosslX509ParseBucket`, and reorders the chain before using the final certificate. For raw credentials, it treats `entity.creds` as an existing `XrdCryptoX509Chain *`.

## State and persistence behavior

The only plugin-local persistent state is the static `gCertfmt`. The function mutates the caller-owned `XrdSecEntity` by assigning a newly allocated `vorg` string. The cache key function allocates the returned key with `new char[]`, matching the main protocol's expectation that `AuthzKey` results are freed with `delete []`.

No files are read by this plugin. PEM parsing allocates a temporary bucket and chain, but the observed implementation does not delete the PEM-mode `XrdSutBucket` and `XrdCryptoX509Chain` on the success path, which is a potential leak.

## Dependencies and integration points

The plugin depends on XRootD version metadata, GSI tracing, `XrdSecEntity`, `XrdSutBucket`, `XrdOucString`, and OpenSSL-backed X.509 parsing through `XrdCryptosslX509ParseBucket`. It integrates only through dynamic symbol lookup by `XrdSecProtocolgsi::LoadAuthzFun`.

In the local `XrdSecgsi/CMakeLists.txt`, the VO authz and DN GMAP modules are built, but this DN authz source is not listed in the visible module targets. That may mean it is legacy, optional, or built elsewhere; packaging should be checked before relying on it.

## Risks and edge cases

- `XrdSecgsiAuthzFun` overwrites `entity.vorg` without freeing an existing value, which can leak if VOMS or prior code already set it.
- The authz decision always returns success and sets a dummy VO, so this plugin should not be treated as an enforcement plugin without modification.
- In PEM mode, success path allocation for the bucket and parsed chain appears not to be released.
- Error paths after `chain->End()` may return without deleting PEM-mode temporary objects.
- Raw mode trusts that `entity.creds` is a valid `XrdCryptoX509Chain *`; using the wrong `certfmt` would reinterpret string memory as a chain pointer.
- `XrdSecgsiAuthzKey` returns `0` on success rather than the DN length; the main protocol treats negative as fatal but also stores the key pointer, so this works for fatal/nonfatal distinction but may not match the documented "return length" expectation.

## Test signals

Tests should load the plugin dynamically through `LoadAuthzFun`, verify `certfmt=raw` and default PEM return values, verify that PEM and raw chains produce the end-proxy subject DN as cache key, and verify failure on missing `key`, missing `entity.creds`, empty chain, parse failure, and empty subject. Memory-sanitizer tests should specifically cover repeated PEM-mode key extraction and repeated authz calls with pre-existing `entity.vorg`.
