# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroons.cc

Purpose: Provides dynamic plugin entry points for Macaroons authorization and HTTP extension handler creation.

Important APIs/types/functions: Exports `XrdAccAuthorizeObjAdd`, `XrdAccAuthorizeObject`, and `XrdHttpGetExtHandler`, with version symbols for all three. Also defines global `XrdSciTokensHelper *SciTokensHelper`.

Control flow: `XrdAccAuthorizeObjAdd` wraps an existing chained authorization object with `Macaroons::Authz`. `XrdAccAuthorizeObject` optionally loads a chained auth library from parameters via `XrdOucPinPath`, `dlopen`, and `dlsym`, otherwise obtains the default authorizer, then wraps it. `XrdHttpGetExtHandler` obtains the default authorizer from the environment and creates a `Macaroons::Handler`.

State and persistence: `SciTokensHelper` is set to each new `Authz` instance, exposing macaroon validation through the SciTokens helper interface. Dynamically loaded chained library handles are not retained in visible state except by the loaded plugin/runtime.

Dependencies and integration points: Integrates XrdAcc authorization ABI, XrdHTTP extension ABI, dynamic loading, default authorization object lookup, `XrdMacaroonsAuthz`, `XrdMacaroonsHandler`, and XRootD version metadata.

Risks: The chained library handle is not closed on success, which is normally needed to keep symbols alive but means process-lifetime residency. Error paths must close handles on failures. Global `SciTokensHelper` can be overwritten if multiple instances are created. Parameter parsing assumes first token is the chained library.

Test signals: Load as primary authz, load with chained authz params, failure to resolve/load chained library, HTTP handler creation with `XrdAccAuthorize*` env pointer, and SciTokens helper validation path.
