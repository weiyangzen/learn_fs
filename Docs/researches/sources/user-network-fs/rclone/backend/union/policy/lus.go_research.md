# sources/user-network-fs/rclone/backend/union/policy/lus.go

Purpose: least-used-space create policy.

Important APIs: `Lus`, registered as `lus`, embeds `EpLus`; overrides `Create`.

Control flow/state: filters creatable upstreams, chooses lowest used-space metric, and returns one upstream.

Dependencies/integration: `context`, `upstream`, `fs`; `TestPolicy1` configures it.

Risks/test signals: unsupported used-space values are attractive because they appear as zero. Contract-level coverage exists through union policy tests.
