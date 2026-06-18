# sources/object-store/garage/src/garage/tests/common/macros.rs

Purpose: This file defines a small async assertion macro for comparing a response body stream against expected bytes.

Important APIs and types: `assert_bytes_eq!` takes a stream expression and expected byte slice/expression. It uses `collect().await`, `into_bytes`, and `assert_eq!`.

Control flow: At expansion sites, the macro awaits body collection, panics on read error, converts to bytes, and compares the byte content to the expected value.

State and persistence behavior: It has no state and no persistence. It consumes the body stream passed into it.

Dependencies and integration points: It relies on `http_body_util::BodyExt` being in scope in the test crate and is imported through `#[macro_use]` in the common module. It is used widely by S3 object, multipart, streaming, SSE-C, and website tests.

Risks: The macro collects full bodies into memory, which is fine for current integration payload sizes but unsuitable for very large streaming tests. It consumes the body, so callers cannot inspect it again.

Test signals: Exact object body comparisons throughout the S3 suites depend on this macro.
