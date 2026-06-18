# sources/user-network-fs/rclone/backend/union/policy/ff.go

Purpose: first-found policy wrapper with custom create behavior.

Important APIs: `FF`, registered as `ff`, embeds `EpFF`; `Create` returns the first creatable upstream.

Control flow/state: create does not check path existence; it only handles empty/no-creatable errors and returns `upstreams[:1]` after filtering.

Dependencies/integration: `context`, `upstream`, `fs`; default union `search_policy`.

Risks/test signals: "first found" for creation means first configured creatable upstream, not existing path. Used broadly by union tests as search policy.
