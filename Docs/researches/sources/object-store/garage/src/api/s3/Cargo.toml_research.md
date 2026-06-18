## sources/object-store/garage/src/api/s3/Cargo.toml

Purpose: Cargo manifest for the `garage_api_s3` library crate.

Important APIs/types/functions: package metadata, library path, workspace lint inheritance, and dependencies for Garage's S3-compatible API server and handlers.

Control flow: build configuration only. `hyper` is server/http1 with default features disabled.

State/persistence: none.

Dependencies/integration: internal workspace dependencies include model/table/block/net/util/rpc/common crates. External dependencies include crypto/checksum, async streams, HTTP/form/multipart/range/XML/JSON parsing, compression, percent encoding, and OpenTelemetry.

Risks: broad dependency surface reflects S3 feature breadth; version changes can affect multipart parsing, range handling, XML compatibility, checksums, and Hyper body behavior.

Test signals: manifest itself has no tests; S3 module tests compile under this dependency set.
