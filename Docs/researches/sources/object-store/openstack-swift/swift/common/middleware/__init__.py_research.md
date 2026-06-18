# sources/object-store/openstack-swift/swift/common/middleware/__init__.py

Purpose: provides shared helpers for Swift middleware modules, currently app attribute forwarding and response-location rewriting support.

Important APIs/types/functions: `app_property(name)` creates a property that forwards access to the wrapped WSGI app. `RewriteContext` extends `WSGIContext` and rewrites `Location` and `Content-Location` response headers from an internal rewritten path back to the originally requested path using a subclass-provided `base_re`.

Control flow: `RewriteContext.__init__` stores requested and rewritten values and compiles a regex from `base_re`. `handle_request` calls the downstream app, scans captured response headers, substitutes matching location values, then calls `start_response` with modified headers and returns the original response iterable.

State and persistence: per-request context stores requested path and compiled rewrite regex. No persistence.

Dependencies and integration: depends on `re` and Swift `WSGIContext`. Used by middleware that internally rewrites request paths but must preserve externally visible redirects or content locations.

Risks: subclasses must provide a correct `base_re`; only `Location` and `Content-Location` headers are rewritten; regex substitution must avoid accidental changes outside the intended URL component; captured response iterators still need normal WSGI close handling. Tests should cover app property forwarding, both rewritten headers, no-match behavior, and subclass regex correctness.
