# sources/user-network-fs/rclone/backend/union/policy/all.go

Purpose: registers and implements union policy `all`, which uses `epall` for action/search but creates on all creatable branches.

Important APIs: `All` embeds `EpAll`; `Create` and `CreateEntries` filter with `filterNC`/`filterNCEntries`.

Control flow/state: empty candidates return `fs.ErrorObjectNotFound`; no creatable candidates return `fs.ErrorPermissionDenied`; otherwise all creatable candidates are returned.

Dependencies/integration: `context`, `upstream`, `fs`, policy registry. `Rand` embeds this policy.

Risks/test signals: intentionally duplicates new files across all eligible branches. Exercised through union policy configurations, especially `TestPolicy3`.
