# sources/object-store/rustfs/crates/protocols/src/swift/router.rs

Implements the Swift URL parser used to classify incoming HTTP requests into account, container, or object operations. It accepts canonical `/v1/AUTH_account/...` paths and an optional configured URL prefix such as `/swift/v1/...`.

Important API surface: `SwiftRoute` carries the parsed account/container/object names plus the HTTP `Method`; `account()` and `project_id()` expose account identity and strip the `AUTH_` prefix using `ACCOUNT_PATTERN`. `SwiftRouter::new()` stores enablement and prefix configuration, while `SwiftRouter::route()` is the main entry point. `decode_url_segment()` percent-decodes path components, and `is_valid_account()` enforces `AUTH_[a-zA-Z0-9_-]+`.

Control flow exits early when disabled, strips the optional prefix with `strip_prefix`, splits on `/` while preserving empty object segments, verifies the first segment is `v1`, then matches exact segment shapes. Account and container trailing slash forms are normalized to account/container routes. Object routes join all remaining decoded segments, preserving consecutive slash semantics in object keys.

State is limited to the router's `enabled` flag and optional prefix; there is no persistence or storage access. Dependencies are `axum::http::{Method, Uri}`, `regex`, `LazyLock`, and `percent_encoding`. The Swift request handler uses this as the front-door path classifier.

Risks: prefix stripping requires `/{prefix}/`, so `/swift` without a slash will not match. Container names are only checked for non-empty segment shape here; deeper Swift naming constraints must live elsewhere. Percent decoding uses lossy UTF-8, which favors routing tolerance over strict rejection.

Test signals cover valid/invalid account patterns, account/container/object routing, prefixed routing, disabled router behavior, and project id extraction.
