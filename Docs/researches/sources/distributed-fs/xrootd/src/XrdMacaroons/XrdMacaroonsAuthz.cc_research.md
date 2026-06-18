# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.cc

Purpose: Implements macaroon-based authorization and token validation for XRootD access operations.

Important APIs/types/functions: Internal `AuthzCheck` verifies `before`, `activity`, `path`, and `name` caveats. `AddPriv` maps `Access_Operation` to `XrdAccPrivs`. `Authz::Access` verifies request-specific or ZTN-session macaroon tokens and grants only the requested operation. `Authz::Validate` minimally validates non-expired session tokens. `validate_verify_empty` accepts path/name/activity caveats for validation-only mode.

Control flow: `Access` bypasses macaroon issuing tests (`AOP_Any`) to the chain, extracts `authz` from env stripping `Bearer%20`, falls back to ZTN entity creds, and on missing/parse failure delegates to configured on-missing behavior. For macaroons, it creates a verifier, installs caveat validators, checks location against `all.sitename`, verifies with the shared secret, logs ID on success, copies `name:` into `Entity->eaAPI` as `request.name`, and returns only the privilege for the requested operation.

State and persistence: `Authz` holds max token duration, chained authorizer, logger, shared secret, location, and on-missing behavior. No token revocation or durable state is stored. Entity attributes may be augmented per request.

Dependencies and integration points: Depends on libmacaroons, XrdAcc, XrdSecEntity attributes, XrdOuc private path helpers (`NormalizeSlashes`, `is_subdirectory`), and `Handler::Config` for shared config parsing. Implements `XrdSciTokensHelper`.

Risks: Location comparison uses `strncmp` with macaroon location size, so a shorter configured location with a longer token location should be reviewed for prefix edge cases. `Entity->creds[Entity->credslen] == '\0'` assumes a readable byte at that index. On failed verification it falls back to chain authz, allowing mixed-token deployments but requiring chain policy to be intentional. Max-duration rejects tokens whose `before` caveat is too far in the future.

Test signals: Caveat verification for expiration, activity mapping, path subtree and substring rejection, stat/mkdir parent allowances, name attribute injection, missing token passthrough/allow/deny, invalid macaroon fallback, wrong location, wrong secret, and `Validate` session-token behavior.
