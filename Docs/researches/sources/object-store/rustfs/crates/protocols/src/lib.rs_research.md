# sources/object-store/rustfs/crates/protocols/src/lib.rs

Purpose: This is the protocols crate root. It denies unsafe code, declares shared and feature-gated protocol modules, and defines the crate's public re-export surface.

Important APIs and types: Always-present modules are `common` and `constants`. Feature-gated modules are `ftps`, `swift`, `webdav`, and `sftp`. Re-exports include `Protocol`, `AuthorizationError`, `ProtocolPrincipal`, `S3Action`, `SessionContext`, `authorize_operation`, plus `FtpsConfig`/`FtpsServer`, `SwiftService`, `WebDavConfig`/`WebDavServer`, and `SftpConfig`/`SftpInitError`/`SftpServer` when their features are enabled.

Control flow: There is no runtime control flow. Compile-time feature flags determine which protocol modules and re-exports are included.

State and persistence behavior: No state or persistence.

Dependencies and integration points: This file is the external API boundary for the protocols crate. Downstream crates can import protocol servers and config types from here instead of navigating internal module paths.

Risks: Re-export changes are semver-relevant for consumers. Feature-gate mismatches between modules and re-exports can break builds. `#![deny(unsafe_code)]` means new unsafe dependencies or blocks in this crate require architectural review rather than local allowance.

Test signals: Full feature-matrix compilation is the main signal. There are no direct tests in this file.
