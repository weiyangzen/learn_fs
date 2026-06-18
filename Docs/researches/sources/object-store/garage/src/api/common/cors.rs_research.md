## sources/object-store/garage/src/api/common/cors.rs

Purpose: implements CORS rule matching and header/preflight response generation for S3-compatible bucket APIs.

Important APIs/types/functions: `find_matching_cors_rule`, `cors_rule_matches`, `add_cors_headers`, `handle_options_api`, and `handle_options_for_bucket`.

Control flow: normal response CORS reads bucket params, validates `Origin`, optional requested headers, and returns the first matching rule. `add_cors_headers` emits wildcard origin or reflects the request origin and adds `Vary: Origin` when reflecting. `handle_options_api` resolves global buckets for unauthenticated preflight; unknown/local bucket names receive permissive wildcard handling. `handle_options_for_bucket` validates required preflight headers, matches configured rules, emits preflight `Vary`, or returns `Forbidden`.

State/persistence: read-only access to bucket CORS config through `BucketParams` and optional global bucket resolution.

Dependencies/integration: used by S3 and K2V API servers before/after auth. Depends on `garage_model::bucket_table::CorsRule`, common helpers, and common error traits.

Risks: unauthenticated OPTIONS cannot resolve local aliases, so fallback is intentionally permissive. Header names and methods are string-matched against stored config; case normalization depends on prior validation. Caches rely on correct `Vary` behavior.

Test signals: local tests cover reflected origin for single/multiple origins, wildcard origin, and preflight `Vary` behavior.
