# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.hh

Purpose: Declares the `Macaroons::Authz` class that wraps XRootD authorization with macaroon validation and also implements `XrdSciTokensHelper`.

Important APIs/types/functions: Constructor takes logger, config, and chained authorizer. Overrides `Access`, `Validate`, `Audit`, `Test`, and `IssuerList`. Private `OnMissing` applies configured behavior when no usable macaroon is present.

Control flow: `Access` and `Validate` are implemented in the `.cc`; `Audit` and `Test` are no-ops returning 0, and `IssuerList` returns empty because macaroons have no issuer concept here.

State and persistence: Holds max duration, chain pointer, logger, secret, location, and authz behavior. No persistence.

Dependencies and integration points: Inherits XrdAcc authorization and SciTokens helper interfaces. Used by plugin entry points in `XrdMacaroons.cc`.

Risks: The class does not own the chained authorizer by smart pointer, so ownership/lifetime are external. Empty issuer list may affect clients expecting token issuer discovery.

Test signals: Construction from config, all overridden interface methods, and chained authorizer lifetime expectations.
