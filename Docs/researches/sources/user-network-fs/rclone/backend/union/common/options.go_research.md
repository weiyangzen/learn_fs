# sources/user-network-fs/rclone/backend/union/common/options.go

Purpose: shared union backend option schema placed in a separate package to avoid import cycles between `union` and `policy`.

Important API: `Options` with `Upstreams`, deprecated `Remotes`, `ActionPolicy`, `CreatePolicy`, `SearchPolicy`, `CacheTime`, and `MinFreeSpace`.

Control flow/state: no runtime logic. `configstruct.Set` populates it in `union.NewFs`, and pointers are passed to upstream wrappers and policies.

Dependencies/integration: imports rclone `fs`; `fs.SpaceSepList` preserves configured remote lists; least-free-space policies read `MinFreeSpace`.

Risks/test signals: config tag drift and backward compatibility with `remotes`. Exercised indirectly by union tests creating synthetic configs.
