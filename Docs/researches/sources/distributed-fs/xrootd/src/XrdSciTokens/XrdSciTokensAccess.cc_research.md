# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensAccess.cc

## Purpose

`XrdSciTokensAccess.cc` implements the SciTokens-based `XrdAccAuthorize` plugin. It validates JWT/SciToken credentials, generates XRootD access rules from token scopes, maps token claims/groups to request names and security-entity attributes, supports chained authorization, exposes a helper validation API, periodically reconfigures issuer/audience policy, and emits optional token monitoring records.

## Important APIs, Types, And Functions

- Local enums `LogMask`, `IssuerAuthz`, and `AuthzBehavior` define logging, issuer authorization strategies, and behavior for missing/invalid token authorization.
- Helpers include `monotonic_time()`, `AddPriv()`, `OpToName()`, `AccessRuleStr()`, `IsSafeUsername()`, `MakeCanonical()`, and `ParseCanonicalPaths()`.
- `MapRule` matches subject, username, path prefix, and group to a result username.
- `IssuerConfig` holds parsed issuer policy: issuer name/url, base/restricted paths, subject mapping behavior, authorization strategy, default user, username/groups claims, and map rules.
- `OverrideINIReader` customizes INI parsing so later duplicate keys override earlier values.
- `XrdAccRules` stores cached parsed token result: expiry, username, token subject, issuer, map rules, groups, authz strategy, and access rules. `apply()` checks operation/path authorization.
- `XrdAccSciTokens` inherits `XrdAccAuthorize`, `XrdSciTokensHelper`, and `XrdSciTokensMon`.
- Public plugin methods include `Access()`, `IssuerList()`, `Validate()`, `Audit()`, `Test()`, and `GetConfigFile()`.
- Private methods include `OnMissing()`, `GenerateAcls()`, `Config()`, `ParseMapfile()`, `Reconfig()`, and `Check()`.
- C plugin exports are `XrdAccAuthorizeObjAdd`, `XrdAccAuthorizeObject`, and `XrdAccAuthorizeObject2`; global symbols `accSciTokens` and `SciTokensHelper` expose singleton/plugin helper state.

## Control Flow

Plugin construction initializes locks, logging, and configuration. `Config()` reads `XRDCONFIGFN` to gather `scitokens.trace`, wires TLS CA settings from the xrootd TLS context when possible, configures key-cache location from `XDG_CACHE_HOME` or `XRDADMINPATH`, then calls `Reconfig()`.

`Access()` extracts a request token from `env["authz"]`, stripping `Bearer%20`, or from ZTN session credentials. Missing token handling delegates to `OnMissing()`. Present tokens are looked up in a 60-second cache keyed by token string; expired or absent entries call `GenerateAcls()`. A successful parsed token becomes an `XrdAccRules` object cached until token expiration or the plugin cap.

Authorization then builds a temporary `XrdSecEntity` carrying issuer in `vorg`, groups in `grps`, and selected attributes. Scope success immediately grants the operation via `AddPriv()`. Mapping or group success can instead chain to the next authorization plugin. When scope or mapping supplies a username, the code writes `request.name` to both the original and temporary entity attribute APIs. It also writes `token.subject` to the original entity. Successful scoped I/O operations can emit token monitoring through `Mon_Report()`.

`GenerateAcls()` first rejects strings that do not look like JWTs. It deserializes with configured valid issuers, checks expiration, creates a SciTokens enforcer with configured audiences, generates ACLs, retrieves issuer config, parses groups/subject/username claim, validates username safety, expands map rules over base paths, applies restricted-path clipping, and maps SciTokens authz strings such as `read`, `create`, `modify`, `write`, `storage.stage`, and `storage.poll` to XRootD operations.

`Reconfig()` parses `/etc/xrootd/scitokens.cfg` by default or `config=<path>` from plugin parameters. It reads global audiences, `audience_json`, `onmissing`, issuer sections, optional JSON map files, base/restricted paths, username/group claims, default user, and authorization strategies, then swaps the config under a write lock. `Check()` opportunistically cleans expired token cache entries and re-runs `Reconfig()` every 60 seconds.

## State And Persistence

The plugin is a process singleton. Runtime state includes config read/write lock, audience and issuer vectors plus C-string arrays passed to SciTokens, parsed-token cache `m_map`, mutexes, chain pointer, parameters, next cleanup time, authz behavior, and config filename. Token cache is in memory only. The SciTokens key cache may persist under `XDG_CACHE_HOME` or `${XRDADMINPATH}/.cache` depending on library support.

## Dependencies And Integration Points

The file depends on XRootD authorization interfaces, `XrdOucEnv`, `XrdOucGatherConf`, `XrdSecEntity`/attributes, TLS context, `INIReader`, `picojson`, `scitokens-cpp`, and monitoring helper classes. It integrates with HTTP via `http.header2cgi Authorization authz`, with chained authorization plugins, with ZTN credentials, with `XrdSecEntityAttr` for request attributes, and with external issuer JWKS discovery through SciTokens.

## Risks And Edge Cases

- `Access()` assumes `Entity` is non-null later even though token extraction checks it conditionally; callers must supply an entity.
- The expression checking ZTN NUL termination indexes `Entity->creds[Entity->credslen]`, which is one byte past a buffer of length `credslen` unless the contract includes an extra NUL.
- Token cache keys are raw token strings and grow until cleanup; high token cardinality can increase memory between checks.
- `IssuerList()` and `Validate()` take config locks but expose C-string arrays derived from vectors; config swaps must preserve array validity during library calls.
- `new_secentity.eaAPI` relies on default construction; cleanup frees only selected C strings, not all copied entity fields because most are borrowed.
- Mapfile parsing accepts `"ignore"` only when it is a string value because non-string handling ignores keys outside a fixed set; boolean ignore may not work.
- `onmissing=allow` is intentionally permissive and should be treated as high-risk config.
- Username claim safety is checked, but default users and mapfile results are not validated by `IsSafeUsername()`.

## Test Signals

Unit tests should cover canonical path normalization, restricted-path clipping, authz string to operation mapping, safe username rejection, JSON mapfile parsing, duplicate INI override behavior, audience and audience_json parsing, authorization strategy parsing, and `onmissing` behavior. Integration tests should run with valid/expired/wrong-issuer/wrong-audience/no-audience tokens; scope-only, group-only, mapping-only, and chained authorization modes; ZTN token credentials; reconfiguration after file changes; and token monitoring output.
