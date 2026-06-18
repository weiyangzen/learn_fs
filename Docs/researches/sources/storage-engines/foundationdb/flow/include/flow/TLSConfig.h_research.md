<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TLSConfig.h -->
# sources/storage-engines/foundationdb/flow/include/flow/TLSConfig.h

Purpose: This header defines TLS configuration loading, peer verification policy, and command-line option metadata for Flow networking. It separates raw configuration paths/bytes from loaded certificate material and provides policy rules for certificate validation.

Important APIs and types: `MatchType`, `X509Location`, `Criteria`, and `TLSEndpointType` describe verification criteria. `LoadedTLSConfig` exposes loaded certificate/key/CA bytes, verify-peer strings, password, plaintext-disable flag, endpoint type, `isTLSEnabled`, and `print`. `TLSConfig` exposes setters for cert/key/CA paths or bytes, password, verify peers, plaintext disablement, synchronous/asynchronous loading, path resolution, and `isInsecure`. `ConfigureSSLContext`, `ConfigureSSLStream`, and `TLSPolicy` handle OpenSSL/Asio integration. `TLSPolicy::Rule` parses verify-peer rules.

Control flow: Callers populate `TLSConfig`, then call `loadSync` or `loadAsync` to produce `LoadedTLSConfig`. Path getters fall back to environment/default config locations. SSL contexts and streams are configured from loaded material and a `TLSPolicy`. Peer verification evaluates certificate chain entries against subject, issuer, root, validity, and time rules and can invoke an `on_failure` callback.

State and persistence behavior: Config state can be in paths or in-memory bytes; loaded state stores certificate material as strings. Persistent data is external certificate/key/CA files. `TLSConfig` mutators keep path and byte forms mutually exclusive per material type.

Dependencies and integration points: It depends on Boost.Asio SSL, OpenSSL X509, Flow networking, knobs, `NetworkAddress`, and command-line option parsing macros. It is central to client/server TLS setup, plaintext-disable policy, and TLS verification metrics.

Risks: `isInsecure` checks only certificate path/bytes, so endpoint and environment behavior must be considered by callers. Verify-peer rule parsing is security-sensitive. Synchronous path resolution can block. Environment fallbacks and default config lookup can make behavior depend on deployment environment. The `TLSPolicy` reference-counted inheritance is private with explicit addref/delref wrappers.

Test signals: Tests should cover path-vs-bytes precedence, sync/async loading, environment/default path fallback, password fallback, plaintext disable flag, SSL context setup, certificate verification rules for exact/prefix/suffix and name/extension locations, failure callbacks, and command-line option parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TLSConfig.h -->
