# sources/user-network-fs/rclone/backend/union/policy/eplno.go

Purpose: existing-path least-number-of-objects policy.

Important APIs: `EpLno`, registered as `eplno`; helpers `lno` and `lnoEntries`.

Control flow/state: `EpAll` narrows candidates, then `GetNumObjects` chooses the smallest reported object count for action/create/search.

Dependencies/integration: `context`, `math`, `upstream`, `fs`; relies on upstream `About`/usage cache.

Risks/test signals: unsupported object counts are logged and effectively treated as zero, biasing selection toward unsupported backends. Tested indirectly.
