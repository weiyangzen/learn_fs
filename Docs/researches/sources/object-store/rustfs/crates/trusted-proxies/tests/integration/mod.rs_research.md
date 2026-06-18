# sources/object-store/rustfs/crates/trusted-proxies/tests/integration/mod.rs

Purpose: Integration test module registry for trusted-proxies.

Important APIs: Under `#[cfg(test)]`, declares `cloud_tests` and `proxy_tests`.

Control flow and state: Compile-time test wiring only. No runtime logic or persistence.

Integration points: Ensures grouped integration tests compile when the test target includes this module.

Risks and tests: No direct behavioral risk. If new integration files are added, they must be registered here or as standalone test targets.
