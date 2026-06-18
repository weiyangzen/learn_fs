# sources/object-store/rustfs/crates/protocols/src/common/session.rs

Purpose: This module defines the authenticated session identity passed through protocol drivers and authorization checks.

Important APIs and types: `Protocol` enumerates `Ftps`, `Swift`, `WebDav`, and `Sftp`. `ProtocolPrincipal` wraps an `Arc<UserIdentity>` and exposes `access_key`. `SessionContext` stores the principal, protocol, and source IP, with constructors and access-key helper. `test_session` builds a minimal test context under `cfg(test)`.

Control flow: Construction is straightforward data wrapping. Consumers build a `SessionContext` after authentication and pass it to gateway authorization. The test helper supplies localhost and default credentials, relying on test authorization overrides rather than real IAM.

State and persistence behavior: There is no persistence. `Arc<UserIdentity>` shares immutable identity data across protocol components for one session. `source_ip` is retained but this file does not enforce IP policy.

Dependencies and integration points: It depends on `rustfs_policy::auth::UserIdentity` and standard IP types. FTPS user-detail construction populates `Protocol::Ftps`; SFTP server/session setup uses `Protocol::Sftp`; gateway support checks branch on `Protocol`.

Risks: Adding a new protocol requires updating exhaustive matches in this module's regression test and in gateway capability checks. `access_key` delegates directly into `UserIdentity.credentials`, so callers must ensure the identity was validated by IAM before use.

Test signals: Compile-time-style regression tests match every `Protocol` variant with no wildcard and assert that `test_session` preserves the supplied protocol.
