# sources/object-store/rustfs/crates/ecstore/src/config/oidc.rs

## Purpose
This file defines default KVS for OpenID Connect identity-provider settings used by server config and admin config.

## Important APIs, types, and functions
`DEFAULT_IDENTITY_OPENID_KVS` contains enable state, config URL, client ID/secret, scopes, audiences, redirect URI fields, claim naming/prefixing, role policy, display name, and groups/roles/email/username claim keys.

## Control flow
There is no algorithm beyond lazy KVS construction. `config::init` registers the defaults, while `config/com.rs` clones them for provider decode, list/boolean normalization, and external `openid` rendering.

## State and persistence behavior
The KVS is static. Actual provider instances are persisted through server config. `OIDC_CLIENT_SECRET` is hidden when empty, but non-empty secrets are still represented in config data.

## Dependencies and integration points
It depends on OIDC constants from `rustfs_config::oidc`, `ENABLE_KEY`, `EnableState`, and `KV/KVS`. Identity setup and admin config rendering consume the resulting config keys.

## Risks and edge cases
Changing default scopes, claim names, or redirect behavior changes login semantics. URL, scope, and claim validation is not done here. Secret safety depends on higher layers respecting redaction and hidden-field behavior.

## Test signals
No local tests. `config/com.rs` covers OIDC decode/encode behavior, including list conversion, booleans, default provider naming, and semantic equality.
