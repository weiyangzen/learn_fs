## sources/security-integrity/cryfs/crates/cli-utils/src/version/mod.rs

Purpose: module hub for version banner and optional update-check support.

Important APIs and exports: always declares `mod version` and re-exports `show_version`. When the `check_for_updates` feature is enabled, it declares `update_checker` and `http_client`, re-exports `ReqwestHttpClient`, and exposes `FakeHttpClient` for tests under `cfg(all(test, feature = "check_for_updates"))`.

Control flow and state: no runtime logic exists. Conditional compilation controls whether network update-check code is part of the crate.

Dependencies and integration: `application.rs` uses `show_version` and, with update checks enabled, `ReqwestHttpClient`. Tests in `version.rs` and `update_checker.rs` use the fake client export.

Risks and test signals: feature gating is the central privacy/reliability switch. Downstream builds that disable default features avoid compiling reqwest/serde_json update-check paths entirely.
