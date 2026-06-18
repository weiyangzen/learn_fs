# sources/object-store/rustfs/crates/trusted-proxies/src/utils/validation.rs

Purpose: General validation utilities for headers, forwarded proxy values, CIDRs, strings, rate-limit/cache parameters, and redaction.

Important APIs/state: `ValidationUtils` with email/URL validation, `validate_x_forwarded_for`, `extract_ip_part`, `validate_forwarded_header`, `validate_ip_in_range`, header checks, port/CIDR/proxy-chain checks, `is_safe_string`, rate/cache parameter validation, and `mask_sensitive_data`. Regexes are cached in `OnceLock`.

Control flow: XFF validation splits comma entries and parses extracted IP parts; bracketed IPv6 is handled, but unbracketed colon splitting favors IPv4-with-port. Header validation enforces name length, value length, and control-character rules. Redaction builds case-insensitive regexes from caller-supplied patterns and logs invalid pattern compilation.

Dependencies and integration: Uses `http::HeaderMap`, `regex`, `ipnetwork`, and tracing. These helpers are public but are not heavily used by the core validator.

Risks and tests: `validate_x_forwarded_for` treats entries with no extractable IP as continue rather than failure in some branches. URL/email regexes are intentionally simple and not standards-complete. Unit validation tests cover representative happy/failure cases for email, URL, XFF, Forwarded, CIDR range, header length, port, and CIDR syntax.
