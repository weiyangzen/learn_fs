# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validation_tests.rs

Purpose: Unit tests for `ValidationUtils`.

Important APIs tested: email/URL validation, X-Forwarded-For validation, RFC7239 Forwarded syntax validation, CIDR membership, header value length/control checks, port validation, and CIDR syntax validation.

Control flow: Each test asserts a simple valid case and, where relevant, a simple invalid case. CIDR membership verifies an IP in `10.0.0.0/8` matches a string list.

State and dependencies: Pure tests with no global mutation. Regex initialization occurs through `OnceLock` in the production module.

Integration points: Confirms public validation utilities compile and handle basic cases.

Risks and coverage gaps: Does not test multiline/control header rejection beyond overlong value, sensitive-data masking, safe-string validation, rate/cache parameter validation, or IPv6/port edge cases in forwarded headers.
