## sources/object-store/garage/src/api/common/Cargo.toml

Purpose: Cargo manifest for the `garage_api_common` library crate that provides shared API server, routing, error, XML, CORS, encoding, and SigV4 utilities.

Important APIs/types/functions: declares package metadata, `lib.rs` path, workspace lint inheritance, and dependencies needed by all common modules.

Control flow: build configuration only. The `hyper` dependency disables default features and enables server/http1, matching the generic server implementation.

State/persistence: none.

Dependencies/integration: internal workspace crates include `garage_model`, `garage_table`, and `garage_util`. External crates include crypto/checksum/signature dependencies (`hmac`, `sha1`, `sha2`, `md-5`, `crc-fast`, `crypto-common`, `hex`, `base64`), async/server stack (`futures`, `tokio`, `http`, `http-body-util`, `hyper`, `hyper-util`, `url`), serialization/docs (`serde`, `serde_json`, `quick-xml`, `utoipa`), and telemetry (`opentelemetry`, `tracing`).

Risks: feature choices and workspace dependency versions affect all API crates. SigV4 and checksum correctness rely on crypto crate behavior; hyper version/API changes affect `generic_server`.

Test signals: no manifest-specific tests; crate tests in common modules exercise code compiled under this manifest.
