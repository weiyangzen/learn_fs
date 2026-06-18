# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensHelper.hh

## Purpose

`XrdSciTokensHelper.hh` declares a helper API exported by the SciTokens authorization plugin so other components can list configured issuers and validate tokens without performing file-operation authorization.

## Important APIs, Types, And Functions

- `struct ValidIssuer` contains `issuer_name` and `issuer_url`.
- `using Issuers = std::vector<ValidIssuer>` is the issuer list return type.
- Pure virtual `IssuerList()` returns configured valid issuers.
- Pure virtual `Validate(token, emsg, expT, entP)` validates token signature/issuer/audience and optionally returns expiration and fills an `XrdSecEntity` with identifying claims.
- Global symbol `SciTokensHelper` is described as the way to find an initialized implementation.

## Control Flow

Callers obtain the plugin-provided instance after the authorization plugin is loaded, then use the virtual API. The implementation in `XrdSciTokensAccess.cc` delegates to `scitoken_deserialize()` and issuer config state.

## State And Persistence

The interface owns no state. Implementations expose plugin runtime state.

## Dependencies And Integration Points

It depends on STL strings/vectors and forward-declares `XrdSecEntity`. It is implemented by `XrdAccSciTokens` and can be used by other XRootD modules needing token validation.

## Risks And Edge Cases

- The helper exists only after plugin load and successful initialization; callers must handle a null global.
- Documentation says issuer list changes only at initialization, but the implementation can reconfigure periodically, so callers should not assume permanent immutability.

## Test Signals

Tests should load the plugin, confirm `SciTokensHelper` is non-null, validate known good/bad tokens, check expiration return, and compare issuer list before and after reconfiguration.
