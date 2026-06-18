<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3token.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/s3token.py

## Purpose
Provides the WSGI middleware that authenticates S3 requests against Keystone's `s3tokens` API. It consumes the auth details prepared by `s3request`, validates or locally revalidates the signature using a cached EC2 secret, injects Keystone identity headers, and rewrites the Swift account path to the authenticated tenant account.

## Important APIs, types, and functions
`parse_v2_response` and `parse_v3_response` map Keystone token responses to `X-Identity-Status`, roles, user, tenant/project, and domain headers. `S3Token.__init__` validates config, builds the Keystone `.../s3tokens` endpoint, configures TLS verification, optional service auth, and optional secret caching. `_json_request` posts credentials to Keystone. `__call__` is the middleware path. `filter_factory` wires paste.deploy configuration.

## Control flow
The middleware purges client-supplied Keystone auth headers unless a prior token has already been set. It ignores non-Swift paths or requests without `s3api.auth_details`. It base64-url encodes the string-to-sign as the Keystone token payload, splits access keys with an optional forced tenant suffix, and checks memcache for `(headers, tenant, secret)`. Cached secrets are accepted only if `check_signature(secret)` succeeds. On cache miss it posts credentials to Keystone, parses v2/v3 JSON, optionally caches the EC2 secret via a Keystone v3 client, stores `keystone.token_info`, injects identity headers, and rewrites `PATH_INFO` from the access-key account to `reseller_prefix + tenant_id`.

## State and persistence behavior
Process state includes request URI, timeout, reseller prefix, TLS verification, service Keystone client, and cache duration. Per-request state is carried in environ and headers. Optional persistence is memcache key `s3secret/<access>` containing parsed headers, tenant, and secret for a bounded duration. It intentionally removes untrusted identity headers from the request boundary.

## Dependencies and integration points
Depends on `requests`, `keystoneauth1`, `keystoneclient.v3`, Swift `Request`, memcache helpers, logging, and `s3request`'s `s3api.auth_details`. Downstream middleware receives Keystone-compatible identity headers and a rewritten account path. The service auth path integrates with Keystone installations that require an authenticated caller for `s3tokens`.

## Risks and test signals
Risks include accepting stale or wrong cached secrets, path rewrite mistakes when account names repeat in the path, service-auth misconfiguration silently disabling caching, and `delay_auth_decision` changing security behavior by forwarding failed auth downstream. Tests should cover v2/v3 response parsing, auth URI validation, TLS option precedence, header purge, cache hit with valid/invalid signature, Keystone non-2xx responses with and without delayed auth, malformed Keystone JSON, forced tenant access keys, and PATH_INFO rewriting with reseller prefix.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3token.py -->
