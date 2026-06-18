# sources/object-store/rustfs/crates/protocols/src/constants.rs

Purpose: This module centralizes small cross-protocol constants for path semantics, network defaults, authentication suffixes, feature-gated protocol defaults, and default bind addresses.

Important APIs and types: `paths` defines root/current/parent/separator strings plus POSIX directory/file type bits and permission triples. `network` defines default bind/source addresses, auth suffixes, and auth failure delay. Feature-gated `ftps`, `webdav`, and `defaults` modules define passive-port parsing constants, WebDAV body/timeout limits, and default FTPS/WebDAV/SFTP listener addresses.

Control flow: There is no executable control flow. Constants are selected at compile time with feature flags such as `ftps`, `webdav`, and `sftp`.

State and persistence behavior: No state or persistence. Values are compile-time constants used by config validation and protocol attribute generation.

Dependencies and integration points: FTPS config uses the passive port separator/count and default address/range. SFTP constants derive POSIX modes from `paths`. Servers use network defaults for source IPs and listener defaults. WebDAV code can use the feature-gated body and request timeout limits.

Risks: Constants encode public behavior and defaults; changing default bind addresses, file modes, or permission triples can affect clients and security posture. Feature gating means missing features remove modules from the public API, so imports must stay gated consistently.

Test signals: Indirect tests in SFTP attributes assert POSIX mode composition. FTPS config tests or startup paths exercise passive port parsing defaults. No direct tests live in this file.
