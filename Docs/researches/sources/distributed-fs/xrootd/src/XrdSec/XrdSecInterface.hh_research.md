# sources/distributed-fs/xrootd/src/XrdSec/XrdSecInterface.hh

Purpose: Defines the public ABI for XRootD security plug-ins and the core authentication/service objects used by clients and servers.

Important APIs and types: `XrdSecBuffer` owns malloc-backed buffers; `XrdSecCredentials` and `XrdSecParameters` alias that buffer type. `XrdSecProtocol` is the per-connection authentication interface, with `Authenticate`, `getCredentials`, optional `Encrypt`/`Decrypt`/`Sign`/`Verify`, session-key methods, `needTLS`, and `Delete`. `XrdSecService` is the server-side factory and policy interface, with `getParms`, `getProtocol`, `PostProcess`, and `protTLS`. Function typedefs `XrdSecGetProt_t` and `XrdSecGetServ_t` describe dynamically loaded factories.

Control flow: Clients consume a server security token with `XrdSecGetProtocol`, generate initial credentials, and loop on `authmore` parameters until authentication completes or fails. Servers send `getParms` output during login, instantiate a protocol from client credentials, call `Authenticate`, and may then run service-level post-processing.

State and persistence: The interface itself has no durable persistence. Protocol objects own per-connection authentication state in `Entity` and optional session keys. Service objects are process-long server singletons in the default loader contract.

Dependencies and integration points: Depends on `XrdSecEntity`, `XrdOucErrInfo`, `XrdNetAddrInfo`, versioned plug-in conventions, and shared libraries named `libXrdSec<p>.so`. It is consumed by protocol plug-ins, `XrdSecServer`, client-side security selection, and request protection.

Risks: The ABI relies on raw pointers, manual `Delete`, malloc/free ownership, and exact exported symbol names. `XrdSecBuffer` frees only the original constructor pointer, so later mutation of `buffer` does not affect ownership. Default crypto methods return `-ENOTSUP`, so protection silently depends on protocol overrides. TLS requirements are split between initializer tokens and `needTLS`.

Test signals: Compile a minimal protocol plug-in with `XrdVERSIONINFO`; exercise multi-step `authmore`, null `einfo`, unsupported crypto, `Delete` lifecycle, TLS-required tokens, and server `PostProcess` rejection.
