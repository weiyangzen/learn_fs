# sources/storage-engines/tikv/components/encryption/export/Cargo.toml

Purpose: This manifest defines `encryption_export`, a crate that reexports selected encryption APIs and wires concrete cloud provider backends for applications and examples outside the core encryption crate.

Important APIs and settings: It uses edition 2021, Apache-2.0, and has an `sm4` feature forwarding to `encryption/sm4`. Dependencies include provider crates `aws`, `azure`, `gcp`, `gcp_v2`, `cloud`, core `encryption`, `file_system`, `kvproto`, `protobuf`, logging, and `tikv_util`. Dev dependencies support the example CLI with `rust-ini` and `structopt`.

Control flow: Cargo resolves provider implementations here, keeping core backend factory code separate from provider-specific crates.

State and persistence behavior: Build metadata only.

Dependencies and integration points: `export/src/lib.rs` uses these dependencies to construct `KmsBackend` instances for AWS, Azure, GCP v1, and GCP v2.

Risks: Provider crate API changes or feature mismatch can break the public factory layer. The forwarded `sm4` feature must stay aligned with core encryption.

Test signals: Provider factory tests and example compilation are the relevant signals.
