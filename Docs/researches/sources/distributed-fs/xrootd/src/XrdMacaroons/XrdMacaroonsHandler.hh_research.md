## sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.hh

Purpose: Declares the `Macaroons::Handler` HTTP extension class and shared macaroon configuration surface used by both request handling and authorization code.

Important APIs and types: Defines `LogMask`, `NormalizeSlashes`, and `Handler`. `Handler` derives from `XrdHttpExtHandler`, exposes `MatchesPath`, `ProcessReq`, `Init`, destructor, and static `Config`. `AuthzBehavior` communicates pass-through, allow, or deny behavior to configuration consumers.

Control flow: The constructor initializes defaults, stores the authorization chain and logger, invokes `Config`, and throws `std::runtime_error` on failure. Private methods separate ID generation, activity derivation, OAuth discovery, OAuth token parsing, response generation, and individual config directive parsing.

State and persistence: Per-instance state is `m_max_duration`, `m_chain`, `m_log`, `m_location`, and `m_secret`. The header itself defines no persistence; secret and location are loaded from configuration by implementation files.

Dependencies and integration points: Depends on `XrdHttp/XrdHttpExtHandler.hh`, forward declarations for authorization, stream, environment, security entity, and standard C++ string/vector. It forms the ABI between XRootD HTTP plugin registration, macaroon authorization, and the configuration parser.

Risks: `m_chain` and `m_log` are raw non-owning pointers with no lifetime enforcement. Throwing from the constructor makes plugin load behavior dependent on callers catching exceptions. Static `Config` is shared by multiple modules, so changes to directive behavior affect issuance and authorization.

Test signals: Compile against plugin registration code; construct with valid and invalid config; verify `AuthzBehavior` values match configuration expectations; ensure `Init` being a no-op is acceptable for the HTTP extension lifecycle.
