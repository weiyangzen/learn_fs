# sources/user-network-fs/rclone/backend/union/policy/epall.go

Purpose: existing-path-all policy. Selects every upstream where the target path, or creation parent path, exists.

Important APIs: `EpAll`, registered as `epall`; helper `epall`; category methods `Action`, `ActionEntries`, `Create`, `CreateEntries`.

Control flow/state: probes upstreams concurrently with `findEntry`, preserves upstream order in results, filters read-only/no-create candidates, and returns not-found or permission errors as needed.

Dependencies/integration: `context`, `path`, `sync`, `upstream`, `fs`; many other policies embed `EpAll`.

Risks/test signals: remote listing latency and case sensitivity affect correctness. Generic union tests use `epall` action in common configs.
