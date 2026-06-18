# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.cc

## Purpose

`XrdSecProtocolgsi.cc` implements the XRootD security protocol plugin named `gsi`. It provides the runtime half of `XrdSecProtocolgsi`: one-time protocol initialization, per-connection protocol object creation, client credential generation, server authentication, post-handshake encryption/signing helpers, X.509 CA/CRL/proxy management, grid-map and authorization plugin integration, and server certificate name validation.

The file is the security-critical implementation for the GSI handshake. It negotiates a crypto backend and symmetric session cipher, exchanges and validates X.509 certificate chains, signs Diffie-Hellman material for newer protocol peers, enforces random-tag challenge/response, optionally maps certificate DNs to local users, optionally extracts VOMS attributes, optionally runs external authorization plugins, and optionally requests or accepts delegated proxies.

## Important APIs, functions, and entry points

- `XrdSecProtocolgsi::XrdSecProtocolgsi(int opts, const char *hname, XrdNetAddrInfo &endPoint, const char *parms)`: constructs a per-connection protocol object, initializes `gsiHSVars`, records the peer host/address, applies DNS trust behavior, and stores initial client-side server parameters when in client mode.
- `XrdSecProtocolgsi::Init(gsiOptions opt, XrdOucErrInfo *erp)`: static one-time configuration. It processes CA/CRL directories, crypto factories, server certificate/key, grid-map service, GMAP/Authz/VOMS plugin loading, proxy delegation options, client proxy/cert/key defaults, DNS trust, hash compatibility, and the server parameter string returned to clients.
- `XrdSecProtocolgsiInit(char mode, const char *parms, XrdOucErrInfo *erp)`: exported C initializer for the plugin. It parses client environment variables or server `sec.protocol ... gsi` parameters into `gsiOptions`, initializes tracing, and calls `Init`.
- `XrdSecProtocolgsiObject(...)`: exported C factory used by the XRootD security framework to instantiate a protocol object.
- `getCredentials(XrdSecParameters *parm, XrdOucErrInfo *ei)`: client-side handshake state machine. It consumes server parameters or continuation messages and emits serialized `XrdSecCredentials`.
- `Authenticate(XrdSecCredentials *cred, XrdSecParameters **parms, XrdOucErrInfo *ei)`: server-side handshake state machine. It consumes client credentials and either returns `kgST_more` with continuation parameters, `kgST_ok`, or `kgST_error`.
- `Encrypt`, `Decrypt`, `Sign`, `Verify`, `getKey`, `setKey`: post-handshake data protection and key export/import methods used after a session key, RSA keys, and message digest have been established.
- `ParseClientInput`, `ClientDoInit`, `ClientDoCert`, `ClientDoPxyreq`: client handlers for server steps `kXGS_init`, `kXGS_cert`, and `kXGS_pxyreq`.
- `ParseServerInput`, `ServerDoCertreq`, `ServerDoCert`, `ServerDoSigpxy`: server handlers for client steps `kXGC_certreq`, `kXGC_cert`, and `kXGC_sigpxy`.
- `AddSerialized`: serializes a main buffer, signs any returned random tag, adds a fresh random challenge, updates the handshake cache, and optionally encrypts the serialized payload into a global bucket.
- `CheckRtag`: validates the random tag returned by the peer by using `sessionKver` to decrypt the signed tag and comparing it to the cached challenge.
- `GetCA`, `VerifyCA`, `LoadCRL`, `VerifyCRL`, `GetCApath`, `ParseCAlist`: CA and CRL discovery, verification, caching, and chain construction.
- `QueryProxy`, `InitProxy`: client/server proxy discovery, proxy creation from user cert/key, validation, export-bucket creation, and proxy cache population.
- `QueryGMAP`, `LoadGMAPFun`, `LoadAuthzFun`, `LoadVOMSFun`: dynamic plugin integration for DN mapping, authorization, and VOMS extraction.
- `GetSrvCertEnt`: server certificate/key loading and cache refresh.
- `ServerCertNameOK`: validates certificate CNs against the requested host and configured `XrdSecGSISRVNAMES`/`-srvnames` style patterns.
- `CopyEntity` and `FreeEntity`: copy/free selected `XrdSecEntity` fields for authz cache persistence.

## Control flow

Initialization starts in `XrdSecProtocolgsiInit`. Client mode reads environment variables such as `XrdSecGSICADIR`, `XrdSecGSIUSERCERT`, `XrdSecGSIUSERKEY`, `XrdSecGSIUSERPROXY`, `XrdSecGSICACHECK`, `XrdSecGSICRLCHECK`, `XrdSecGSIDELEGPROXY`, `XrdSecGSICREATEPROXY`, `XrdSecGSISRVNAMES`, `XrdSecGSIUSEDEFAULTHASH`, and `XrdSecGSITRUSTDNS`. Server mode tokenizes plugin parameters such as `-certdir`, `-crldir`, `-cert`, `-key`, `-cipher`, `-md`, `-ca`, `-crl`, `-gridmap`, `-gmapfun`, `-authzfun`, `-authzcall`, `-authzpxy`, `-vomsat`, `-vomsfun`, `-dlgpxy`, `-exppxy`, `-defaulthash`, `-trustdns`, and `-showdn`.

`Init` then establishes static protocol state. On servers it loads crypto factories from the configured list, filters cipher and message-digest lists by backend support, loads and validates server certificate/key entries into `cacheCert`, initializes grid-map handling, loads optional plugin entry points, configures delegated proxy export behavior, and returns the advertised server options string `v:<version>,c:<cryptomod>,ca:<issuer-hashes>`. On clients it resolves proxy/cert/key defaults and delegation preferences and returns an empty parameter string.

The client handshake begins in `getCredentials`. On the initial `kXGS_init` exchange, `ClientDoInit` reads the server version, selected crypto list, and server CA list, chooses a crypto factory, loads the relevant CA, and obtains a user proxy chain from `QueryProxy`. The client sends version, crypto module, issuer hash, options, and then requests the server certificate. On `kXGS_cert`, `ClientDoCert` validates the cached handshake, verifies the server certificate chain and host identity, extracts the server signing key, verifies signed DH material when supported, creates the session cipher, chooses a digest, and sends the client certificate chain. If the server asks for proxy delegation with `kXGS_pxyreq`, `ClientDoPxyreq` either forwards the private key of the local proxy or signs a server-created proxy request, depending on negotiated options.

The server handshake begins in `Authenticate`. `ServerDoCertreq` processes the initial client request: it reads client version/options, selects the crypto module, loads the CA for the client issuer hash, finds the server certificate entry, and prepares a main buffer. The `kXGC_certreq` response sends signed server DH parameters, supported cipher/digest lists, and the server certificate. `ServerDoCert` then accepts the client certificate exchange: it finalizes the cipher with client DH data, decrypts the main buffer, parses and verifies the client chain, checks the client public key consistency for signed-DH peers, creates any delegated-proxy request state, and instantiates the chosen message digest. `Authenticate` then maps the user, fills `Entity`, optionally exports DN monitoring info, runs VOMS extraction, runs authorization cache/plugin logic, optionally exports proxy material into `Entity.creds` or `Entity.endorsements`, and either succeeds or asks for one more `kXGS_pxyreq` exchange. `ServerDoSigpxy` finishes delegated proxy creation or proxy forwarding and may save the proxy in memory, `Entity.creds`, or a resolved file path.

Errors consistently route through `ErrF`, `ErrC`, and `ErrS`, which populate `XrdOucErrInfo` and release temporary buffers. Successful handshakes delete `hs`; failed paths return null credentials or `kgST_error`.

## State and persistence behavior

The file relies on extensive static process-wide state: CA/CRL directories, server/user certificate paths, proxy defaults, crypto factory arrays, grid-map/authz/VOMS plugin function pointers, tracing handles, DNS trust flags, and caches. Main caches include `cacheCA` for CA chains and CRLs, `cacheCert` for server certificates, `cachePxy` for client proxies, `cacheGMAPFun` for plugin DN mapping results, and `cacheAuthzFun` for authorization plugin output. Cache entries store raw pointers in `buf1`/`buf2`/`buf3`/`buf4`, status values, modification/expiry times, and are protected by `XrdSutCERef` locks.

`gsiHSVars` is per-handshake state. It holds the current step, timestamp, remote version, selected crypto module, reference cipher, certificate/proxy chains, CRL pointer, random tag cache reference, proxy delegation options, and buffered initial parameters. Its destructor releases or detaches chains and CRLs according to ownership flags.

`Entity` is per-protocol-instance XRootD identity state. The code mutates `Entity.name`, `host`, `vorg`, `role`, `grps`, `creds`, `endorsements`, `moninfo`, and entity attributes as authentication progresses. `Delete()` frees these fields, handshake state, session crypto objects, delegated proxy chains, and expected host memory before deleting `this`.

Persistent filesystem interactions include loading CA files from `CAdir`, CRLs from `CRLdir`, server/user certs and keys, grid-map files, user proxy files, optional `.crl_url` files, and delegated proxy output files. `InitProxy` may create or refresh a proxy file through the crypto backend. `ServerDoSigpxy` may write a delegated proxy chain to a resolved path with `<uid>`/identity substitutions.

## Dependencies and integration points

This implementation is tightly integrated with XRootD's security and utility layers: `XrdSecProtocol`, `XrdSecCredentials`, `XrdSecParameters`, `XrdSecEntity`, `XrdOucErrInfo`, `XrdOucTokenizer`, `XrdOucGMap`, `XrdOucPinLoader`, `XrdSutBuffer`, `XrdSutBucket`, `XrdSutCache`, `XrdSutPFEntry`, `XrdSutRndm`, `XrdCryptoFactory`, `XrdCryptoCipher`, `XrdCryptoRSA`, `XrdCryptoX509`, `XrdCryptoX509Chain`, `XrdCryptoX509Req`, `XrdCryptoX509Crl`, and tracing macros from `XrdSecgsiTrace.hh`.

Externally visible plugin integration depends on C symbols:

- `XrdSecProtocolgsiInit`
- `XrdSecProtocolgsiObject`
- GMAP plugin symbol `XrdSecgsiGMAPFun`
- Authz plugin symbols `XrdSecgsiAuthzFun`, `XrdSecgsiAuthzKey`, `XrdSecgsiAuthzInit`
- VOMS plugin symbols `XrdSecgsiVOMSFun`, `XrdSecgsiVOMSInit`

Build integration in `src/XrdSecgsi/CMakeLists.txt` compiles this file and the header/options header into the main `XrdSecgsi-${PLUGIN_VERSION}` module linked against `XrdCrypto` and `XrdUtils`.

## Risks and edge cases

- This is security-sensitive code with manual memory management. Ownership of `Entity.creds`, X.509 chains, cached pointers, and buckets varies by path; regressions can cause leaks, double frees, stale pointer use, or accidental failure to free credentials.
- The protocol has backward compatibility branches for old peers that do not sign DH material. In those paths it disables proxy delegation, but cipher/session negotiation still has legacy complexity and should be tested carefully.
- Hostname verification intentionally has DNS fallback when `TrustDNS` is true. Delegation is disabled if DNS fallback was used, but host identity behavior is subtle and depends on SAN presence, CN format, `expectedHost`, and configured allowed-name patterns.
- Authz cache expiration logic uses both configured timeout and end-proxy `NotAfter`; incorrect interpretation can preserve stale authorization state or force excessive plugin calls.
- `QueryProxy` can source credentials from `XrdSecCREDS`, proxy files, cert/key files, or generated proxies. Each path has different assumptions about key presence, chain length, and file permissions.
- CRL behavior is configurable from ignore to require/update. Downloading CRLs from certificate URI or `.crl_url` files affects availability and may block authentication if remote or file data is stale or malformed.
- Some parameter parsing has legacy quirks. For example, server `-ca:` first calls `getOptVal(caVerOpts, op+4)` but then assigns `atoi(op+4)`, so symbolic values like `verifyss` appear vulnerable to being overwritten as zero. That should be reviewed against expected configuration behavior.
- `ServerDoSigpxy` returns success-like local control (`0`) for several delegation failures by setting `cmsg`; callers may still complete authentication without delegated proxy material. This is intentional for optional delegation but risky if operators assume delegation is mandatory.
- The caches store raw pointers with custom lifetime management and reference stacks. Thread-safety depends on correct `XrdSutCache` locking and `GSIStack` reference counting.

## Test signals

Useful tests should include full client/server handshake success using valid CA/server/client certs, failure on missing CA, expired certificate, bad CRL, wrong host SAN/CN, unsupported crypto/cipher/digest, and random-tag mismatch. Compatibility tests should cover peers below and above `XrdSecgsiVersDHsigned` and `XrdSecgsiVersCertKey`.

Operational tests should exercise environment-driven client proxy paths, URL-supplied `xrd.gsiusrpxy`/`xrd.gsiusrcrt`/`xrd.gsiusrkey`, `XrdSecCREDS`, pure cert/key authentication, auto proxy creation, and non-tty behavior. Server tests should cover grid-map optional vs required modes, DN-hash vs DN-name fallback, GMAP plugin cache expiration, authz plugin success/failure/cache hit/cache expiry, VOMS extract vs require behavior, proxy export to `Entity.creds`/`endorsements`, delegated proxy request/signing, forwarded proxy, and file export with `<uid>` substitution.

Regression tests should explicitly verify that proxy delegation is disabled when hostname validation used DNS fallback or unsigned DH parameters, that `-ca:` symbolic values map correctly, and that `Delete()`/failed handshake paths do not leak or double-free via sanitizers.
