# sources/user-network-fs/rclone/backend/union/policy/mfs.go

Purpose: most-free-space create policy and common/default placement behavior.

Important APIs: `Mfs`, registered as `mfs`, embeds `EpMfs`; overrides `Create`.

Control flow/state: filters creatable upstreams, chooses largest free-space metric, and returns one upstream.

Dependencies/integration: `context`, `upstream`, `fs`; linked to default union creation semantics.

Risks/test signals: unsupported free-space metrics and cache staleness can skew branch choice. Generic union tests cover default behavior.
