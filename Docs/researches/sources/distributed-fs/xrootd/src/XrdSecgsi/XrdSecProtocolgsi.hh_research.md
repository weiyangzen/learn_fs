# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.hh

## Purpose

`XrdSecProtocolgsi.hh` declares the GSI security protocol interface, constants, handshake enums, option carrier, plugin callback types, proxy helper structs, reference stack helper, `XrdSecProtocolgsi` class, and `gsiHSVars` handshake-state class. It is the shared contract used by `XrdSecProtocolgsi.cc` and any code that instantiates or interacts with the `gsi` security plugin.

## Important APIs, types, and constants

- `XrdSecPROTOIDENT`, `XrdSecPROTOIDLEN`, `XrdSecgsiVERSION`, `XrdSecNOIPCHK`, `XrdSecDEBUG`, `XrdCryptoMax`, and protocol feature version constants define protocol identity, versioning, flags, and compatibility gates.
- `kgsiStatus` defines server return status: error, ok, or more data required.
- `kgsiClientSteps` and `kgsiServerSteps` define the client/server handshake step IDs. Client steps are certificate request, certificate packet, and signed proxy packet; server steps are init, certificate packet, and proxy request.
- `kgsiHandshakeOpts` defines delegation and proxy flags such as delegated proxy request, proxy forwarding, signing request acceptance, server request, save-to-file, save-as-credentials, proxy creation, and ownership cleanup.
- `kgsiErrors` enumerates protocol-specific error codes used by `ErrF`, `ErrC`, and `ErrS`.
- Plugin callback typedefs declare external dynamic plugin contracts: `XrdSecgsiGMAP_t`, `XrdSecgsiAuthz_t`, `XrdSecgsiAuthzInit_t`, `XrdSecgsiAuthzKey_t`, and aliases for VOMS extraction.
- `gsiOptions` is the initialization option bundle used by `XrdSecProtocolgsi::Init`. It holds client/server settings for crypto modules, CA/CRL paths, cert/key/proxy paths, proxy validity/depth/bits, grid-map files and functions, authorization functions, authz cache behavior, delegation behavior, VOMS extraction, monitoring information, DNS trust, hash compatibility, and DN display.
- `ProxyOut_t` and `ProxyIn_t` pass proxy chain/key/export information into and out of `QueryProxy` and `InitProxy`.
- `GSIStack<T>` wraps an `XrdOucHash<T>` plus mutex to track shared CA/CRL objects by pointer string. It adds entries with an extra count and decrements references on deletion.
- `XrdSecProtocolgsi` subclasses `XrdSecProtocol` and exposes `Authenticate`, `getCredentials`, crypto helpers, session key helpers, `Init`, `Delete`, and `EnableTracing`.
- `gsiHSVars` stores per-handshake mutable state such as selected crypto module, remote version, reference cipher, exported certificate bucket, cache entry, CA chain, CRL, proxy chain, random-tag status, last step, options, peer hash algorithm, and buffered parameters.

## Control flow represented by declarations

The header splits public framework-facing methods from private state-machine helpers. Public methods implement the XRootD security interface. Private client handlers parse server messages and generate the next client response, while private server handlers parse client messages and produce continuation data or final identity state. Auxiliary methods handle crypto parsing, CA loading, CRL loading, proxy loading, dynamic plugin loading, error reporting, random-tag checks, server certificate name validation, grid-map lookup, and entity copying.

The header also encodes lifecycle expectations. The normal C++ destructor is empty because callers are expected to invoke `Delete()`, which frees protocol-owned resources and deletes the object. `gsiHSVars` owns cleanup of temporary handshake objects and uses option flags to decide whether chains and proxies are owned by the handshake or by caches.

## State and persistence behavior

Most persistent process state is declared as static members of `XrdSecProtocolgsi`: paths, default options, crypto factories, reference ciphers, caches, grid-map service, CA/CRL stacks, plugin function pointers, trace/logger objects, and runtime flags. Per-instance state includes endpoint address, session crypto objects, delegated proxy chain, expected hostname, IV behavior, URL-specified credential paths, and the active `gsiHSVars` pointer.

The header makes clear that cache data and handshake data share objects: CA chains and CRLs may be referenced from caches and tracked by `GSIStack`, while proxy chains may be owned by `cachePxy`, the handshake, or the protocol instance depending on `kOptsDelPxy` and delegation completion.

## Dependencies and integration points

The header includes XRootD networking (`XrdNetAddrInfo`), utility (`XrdOuc*`), system synchronization (`XrdSysPthread`), security interface (`XrdSecInterface`), GSI tracing, SUT cache/buffer/random utilities, and crypto factory/X.509/CRL/chain types. It defines the binary and source-level contract for the main `secgsi` plugin module and for dynamic GMAP/Authz/VOMS modules loaded by the implementation.

## Risks and edge cases

- The class uses numerous static mutable members, so initialization order, test isolation, and repeated initialization in one process are important risks.
- Ownership flags in `gsiHSVars` (`kOptsDelChn`, `kOptsDelPxy`) are essential for avoiding deletion of cached chains; misuse can corrupt shared cache state.
- `GSIStack` tracks objects by formatted pointer string and relies on `Hash_count`; pointer reuse or mismatched add/delete calls would be hard to debug.
- The empty C++ destructor combined with `Delete()` can surprise maintainers. Deleting an `XrdSecProtocolgsi` through normal C++ deletion would skip cleanup logic.
- `gsiOptions` contains raw `char *` pointers and comments that cleanup happens in `XrdSecProtocolgsiInit`, so copy/lifetime assumptions matter during parsing.

## Test signals

Tests should compile plugin consumers against this header and verify ABI symbols through the exported C factory/init functions. Runtime tests should inspect `Delete()` cleanup rather than relying on the C++ destructor. Handshake tests should exercise all declared step transitions and option flags, especially proxy delegation flags and cleanup flags. Static-analysis or sanitizer runs should focus on raw-pointer fields in `gsiOptions`, `gsiHSVars`, caches, and `Entity`.
