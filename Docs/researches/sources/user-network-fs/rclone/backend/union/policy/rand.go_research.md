# sources/user-network-fs/rclone/backend/union/policy/rand.go

Purpose: random policy across all eligible candidates, using `All` for create/action behavior and existing-path search.

Important APIs: `Rand`, registered as `rand`; `rand`, `randEntries`, and category overrides.

Control flow/state: `All` collects eligible action/create candidates, `epall` collects search candidates, then one random candidate is returned.

Dependencies/integration: `context`, `math/rand`, `upstream`, `fs`; `TestPolicy2` uses `create_policy=rand`.

Risks/test signals: nondeterministic placement with global RNG. Tests should verify contract behavior only.
