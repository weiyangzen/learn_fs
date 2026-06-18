# sources/object-store/openstack-swift/swift/common/middleware/domain_remap.py

## Purpose
`domain_remap.py` translates account and optional container names embedded in the request host into Swift path components. It supports virtual-host style URLs such as `container.AUTH-account.example.com/object` and account-only hosts.

## Important APIs, Types, and Functions
`_DomainRemapContext` specializes `RewriteContext`. `DomainRemapMiddleware` parses storage domains, path root, reseller prefixes, default reseller prefix, and client path mangling settings. `filter_factory()` registers `domain_remap` info and returns the filter.

## Control Flow
On each request, the middleware extracts `HTTP_HOST` or `SERVER_NAME`, strips a port, and finds a configured storage-domain suffix. The host prefix must contain one or two labels: account or container plus account. Account names have one hyphen converted to underscore and reseller prefix case normalized. If the account prefix is unknown, a configured default reseller prefix may be prepended; otherwise the request passes through. The new path is built as `/<path_root>/<account>/<container?>/<old path>`, optionally stripping an existing path root from the client path, then `PATH_INFO` is updated and `RewriteContext` handles response rewriting.

## State and Persistence
All state is process-local configuration. The middleware mutates the request environ path for downstream handling and persists no Swift metadata.

## Dependencies and Integration Points
It uses Swift `RewriteContext`, `Request`, `HTTPBadRequest`, `wsgi_quote`, config parsing, CSV list parsing, and Swift registry. It commonly runs after CNAME lookup so vanity domains first map to a storage domain.

## Risks and Edge Cases
Host-derived account and container names must be DNS-compatible and are best-effort only. More than two host labels before the storage domain returns `400`. Browser lowercasing requires prefix case repair. `mangle_client_paths` changes how existing `/v1` path roots are treated and can affect compatibility. Host header trust and proxy configuration are security-sensitive.

## Test Signals
Tests should cover account-only and container/account hosts, bad label counts, storage-domain normalization, ports, reseller prefix case repair, hyphen-to-underscore conversion, default reseller prefix, unknown-prefix pass-through, path-root insertion and mangling, no storage-domain pass-through, and rewrite context behavior.
