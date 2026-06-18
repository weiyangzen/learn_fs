# sources/user-network-fs/rclone/backend/union/policy/lno.go

Purpose: least-number-of-objects create policy.

Important APIs: `Lno`, registered as `lno`, embeds `EpLno`; overrides `Create`.

Control flow/state: filters creatable upstreams and selects the lowest object-count metric without requiring existing parent path.

Dependencies/integration: `context`, `upstream`, `fs`; reuses `eplno` helpers.

Risks/test signals: unsupported object count maps to zero and can bias selection. Coverage is indirect.
