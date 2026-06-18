## sources/object-store/garage/src/api/admin/openapi.rs

Purpose: defines the utoipa OpenAPI surface for Garage's v2 administration API. The file is mostly documentation metadata and schema glue: `#[utoipa::path]` functions are zero-body marker functions used by the `#[derive(OpenApi)]` block on `ApiDoc`.

Important APIs/types/functions: marker functions cover special endpoints (`Metrics`, `Health`, `CheckDomain`), cluster status/statistics/connect, admin token CRUD, layout operations, access key CRUD, bucket operations, permissions, aliases, node, worker, and block maintenance APIs. `UpdateClusterLayoutRequestOpenapi` and `NodeRoleChangeOpenapi` replace the runtime request shape for generator compatibility with flattened untagged enums. `BucketAliasEnumOpenapi` similarly documents global/local alias request alternatives. `SecurityAddon` injects the `bearerAuth` HTTP security scheme.

Control flow: there is no runtime request handling here. Utoipa macros collect marker functions into `ApiDoc`, apply global bearer security, and register a local server URL. Security is overridden for public special endpoints where declared with `security(())`.

State/persistence: none directly. The documented endpoints map to handlers elsewhere that mutate cluster layout, keys, buckets, workers, repair state, or block metadata.

Dependencies/integration: depends on `crate::api::*` request/response schemas, `serde`, `utoipa::{OpenApi, ToSchema, Modify}`, and feeds admin API documentation generation.

Risks: documentation can drift from `router_v2.rs` and handler semantics because paths and request bodies are manually enumerated. Workaround schema types must remain equivalent to runtime types. The OpenAPI version string is hard-coded as `v2.3.0`.

Test signals: no local tests. Validation is compile-time macro expansion and downstream OpenAPI generation; route parity should be checked against `AdminApiRequest::from_request`.
