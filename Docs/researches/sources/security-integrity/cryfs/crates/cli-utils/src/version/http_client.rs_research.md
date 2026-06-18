## sources/security-integrity/cryfs/crates/cli-utils/src/version/http_client.rs

Purpose: abstraction for HTTP GET requests used by update checking, plus a reqwest implementation and test fake.

Important APIs and types: `HttpClient` trait exposes `get(&self, url, timeout) -> Result<String>`. `ReqwestHttpClient` builds a blocking reqwest client, performs a GET with timeout, and returns response text. Test-only `FakeHttpClient` maps URLs to content and counts requests through an `AtomicUsize`.

Control flow and state: production requests create a fresh reqwest blocking client per call. The fake stores website bodies in a `HashMap` and increments request count for every attempted URL, returning an `anyhow` error when unknown.

Dependencies and integration: depends on optional `reqwest` for production, `anyhow`, `Duration`, and test synchronization primitives. `update_checker` uses the trait; `version.rs` injects `ReqwestHttpClient` from the CLI runner.

Risks and test signals: tests include fake behavior and live reqwest checks against invalid protocols/domains and example.com. Live network tests can be flaky in offline or filtered environments. The abstraction keeps update-check parsing testable without network access.
