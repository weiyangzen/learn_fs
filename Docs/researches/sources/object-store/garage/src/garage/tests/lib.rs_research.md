# sources/object-store/garage/src/garage/tests/lib.rs

Purpose: This is the integration test crate root for the Garage binary/API tests.

Important APIs and types: It imports `common` with macros, declares `admin`, `bucket`, `s3`, and feature-gated `k2v` and `k2v_client` modules. It also defines async helper `json_body` for collecting Hyper responses into `serde_json::Value`.

Control flow: Module declarations determine test discovery. `json_body` consumes a response body, collects it, parses JSON, and returns the parsed value.

State and persistence behavior: The root has no persistent state. Its modules create and mutate live Garage state through the common context.

Dependencies and integration points: It depends on `http_body_util::BodyExt`, Hyper `Body`/`Response`, `serde_json`, and the common harness. It is the top-level integration point for all tests in `garage/tests`.

Risks: Feature-gated K2V tests are absent unless the `k2v` feature is enabled. `json_body` unwraps collection and parsing, so malformed responses panic rather than producing richer diagnostics.

Test signals: Successful compilation of this root wires all child modules and shared helpers into the Rust test runner.
