# sources/user-network-fs/rclone/backend/union/policy/eplfs.go

Purpose: existing-path least-free-space policy.

Important APIs: `EpLfs`, registered as `eplfs`; `lfs`, `lfsEntries`, and category methods. Defines `errNoUpstreamsFound`.

Control flow/state: delegates to `EpAll` for existence/permission filtering, then picks the candidate with least free space above `MinFreeSpace`.

Dependencies/integration: `context`, `errors`, `math`, `upstream`, `fs`; depends on upstream usage cache and `GetFreeSpace`.

Risks/test signals: unsupported free-space metrics are treated as effectively infinite by upstream wrappers; `min_free_space` can reject all candidates. Coverage is indirect.
