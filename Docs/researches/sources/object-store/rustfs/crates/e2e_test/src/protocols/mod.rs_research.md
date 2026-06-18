# sources/object-store/rustfs/crates/e2e_test/src/protocols/mod.rs

Purpose: module root for protocol E2E tests covering FTPS, SFTP, and WebDAV.

Important APIs/types/functions: publicly exposes `ftps_core`, `sftp_compliance`, `sftp_core`, `sftp_helpers`, `test_env`, `test_runner`, and `webdav_core`; declares private `sftp_compliance_tests` implementation modules.

Control flow: this root controls which protocol modules are compiled and which helpers are externally reusable inside the e2e crate. Public entry modules expose async suite functions, while private compliance case bodies stay internal.

State and persistence behavior: none locally. Child modules start RustFS protocol listeners, create temp data directories, seed S3 objects, and own process teardown.

Dependencies and integration points: ties protocol-specific test suites into the e2e crate. The public/private split lets high-level compliance entries call detailed cases without making every case module part of the public test API.

Risks: low, but module visibility changes can affect downstream test runner access. Missing declarations would drop whole protocol suites from compilation.

Test signals: module discovery and organization signal only; concrete protocol behavior is tested in child modules.
