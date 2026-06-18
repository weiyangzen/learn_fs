# Research: sources/object-store/minio-mc/cmd/ilm-rule-add.go

Purpose: implements `mc ilm rule add`, adding lifecycle expiration, transition, and noncurrent-version actions to a bucket.

Important APIs/types/functions: `ilmAddCmd`, `ilmAddFlags`, `ilmAddMessage`, `checkILMAddSyntax`, and `mainILMAdd`.

Control flow: validates one target, fetches existing lifecycle config, treats `NoSuchLifecycleConfiguration` as an empty config, parses CLI flags into `ilm.LifecycleOptions`, converts them to a validated `lifecycle.Rule`, appends the rule, writes via `SetLifecycle`, and prints the generated or supplied rule ID.

State and persistence: mutates bucket lifecycle configuration server-side.

Dependencies/integration points: relies heavily on `cmd/ilm` parsing and validation helpers, MinIO `lifecycle` types, and `minio.ToErrorResponse` for absent config.

Risks: read-append-write can race with concurrent lifecycle edits. Deprecated and current flags coexist, so parser changes must preserve compatibility. Generated IDs are xid strings.

Test signals: parser unit tests exist for filters; CLI-level add should be tested with no existing config and representative action combinations.
