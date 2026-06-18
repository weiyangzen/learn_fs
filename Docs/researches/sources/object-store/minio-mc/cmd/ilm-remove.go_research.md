# Research: sources/object-store/minio-mc/cmd/ilm-remove.go

Purpose: implements `mc ilm rule remove`/`rm`, removing one lifecycle rule by ID or all rules with explicit force.

Important APIs/types/functions: `ilmRemoveFlags`, `ilmRmCmd`, `ilmRmMessage`, `checkILMRemoveSyntax`, and `mainILMRemove`.

Control flow: syntax requires one target. `--all` and `--force` must be supplied together; otherwise `--id` is required. The handler fetches current lifecycle config, either clears `Rules` or calls `ilm.RemoveILMRule`, writes back with `SetLifecycle`, and prints success.

State and persistence: mutates bucket lifecycle configuration on the target server.

Dependencies/integration points: uses `newClient`, MinIO client `GetLifecycle`/`SetLifecycle`, and helper package `cmd/ilm`.

Risks: `--all --force` clears all rules. Removal is read-modify-write and can overwrite concurrent lifecycle changes. Empty config semantics depend on server `SetLifecycle`.

Test signals: no direct tests; helper `RemoveILMRule` deserves unit coverage for nil/empty/not found. CLI tests should verify force coupling.
