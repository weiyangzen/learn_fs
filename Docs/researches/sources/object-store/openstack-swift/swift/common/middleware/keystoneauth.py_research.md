# sources/object-store/openstack-swift/swift/common/middleware/keystoneauth.py

## Purpose
`keystoneauth.py` is Swift's authorization middleware for Keystone-authenticated identities. It consumes identity headers produced by `keystonemiddleware.auth_token`, maps Keystone projects to reseller-prefixed Swift accounts, installs `swift.authorize`, and implements role, ACL, service-token, system-reader, and anonymous/referrer authorization rules.

## Important APIs, Types, and Functions
Constants define project domain-id client and sysmeta headers plus an unknown sentinel. `KeystoneAuth.__call__()` extracts identity and installs authorization hooks. `_keystone_identity()` parses Keystone v2/v3 identity and service roles. `_set_project_domain_id()` persists account project-domain sysmeta when possible. `_authorize_cross_tenant()`, `authorize()`, `authorize_anonymous()`, `_authorize_unconfirmed_identity()`, and `denied_response()` implement access policy.

## Control Flow
On each request, the middleware honors `swift.authorize_override` when configured, otherwise extracts confirmed identity and service identity headers. Confirmed users get `REMOTE_USER`, `keystone.identity`, `swift.authorize`, optional `reseller_request`, access-log user id, and ACL cleaning. Anonymous users get `authorize_anonymous`. The start_response wrapper exposes project-domain sysmeta as a client header. Authorization parses the Swift path, handles OPTIONS, sets project-domain id metadata on account/container create/update paths, grants reseller-admin and read-only system-reader access, denies non-admin own-account DELETE, checks cross-tenant ACLs, referrer/container-sync ACLs, account/project match, operator roles plus optional service roles, project-reader roles for GET/HEAD, and finally ACL role matches before returning 401/403.

## State and Persistence
Configuration is process-local. Project domain id may be persisted as account sysmeta to support name-based ACL compatibility. Request-local authorization state is stored in environ keys such as `swift.authorize`, `swift_owner`, `reseller_request`, `keystone.identity`, and `swift.access_logging`.

## Dependencies and Integration Points
It depends on Keystone auth-token headers and token info, Swift ACL parsing/cleaning, reseller option parsing, account info lookup, system metadata prefixes, and Swift HTTP response classes. It integrates with formpost/tempurl through authorize overrides and with container sync through unconfirmed identity checks.

## Risks and Edge Cases
Role configuration is prefix-specific and backwards-compatible defaults can be subtle. Name-based ACL compatibility is domain-sensitive and can be disabled. Project-domain metadata may be unknown when reseller admins create accounts for other projects. Service-token requirements change owner semantics. Anonymous authorization is authoritative only for configured reseller prefixes. Incorrect pipeline ordering with authtoken or override-capable middleware changes security behavior.

## Test Signals
Tests should cover identity extraction for v2/v3 and service tokens, override behavior, reseller admin and system reader grants, own-account DELETE denial, account/project matching, operator roles with and without service roles, project reader GET/HEAD behavior, cross-tenant id/name/wildcard ACLs with domain compatibility, referrer ACLs, container-sync key authorization, project-domain sysmeta set/expose paths, anonymous auth, 401 vs 403 denial, and prefix-specific config.
