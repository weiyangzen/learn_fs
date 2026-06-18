# sources/user-network-fs/rclone/backend/union/policy/lfs.go

Purpose: least-free-space create policy without existing-path filtering.

Important APIs: `Lfs`, registered as `lfs`, embeds `EpLfs`; overrides `Create`.

Control flow/state: filters creatable upstreams, then uses `lfs` to select the least free space above `min_free_space`.

Dependencies/integration: `context`, `upstream`, `fs`; reuses `eplfs` helpers.

Risks/test signals: can deliberately choose a nearly full backend; metric support and cache freshness matter. Tested indirectly.
