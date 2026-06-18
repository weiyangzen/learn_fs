# sources/user-network-fs/rclone/backend/union/policy/eprand.go

Purpose: existing-path random policy.

Important APIs: `EpRand`, registered as `eprand`; random helpers over upstream and entry slices.

Control flow/state: calls `EpAll`/`epall` to collect eligible existing candidates, then returns a single `math/rand.Intn` choice.

Dependencies/integration: `context`, `math/rand`, `upstream`, `fs`.

Risks/test signals: nondeterministic and uses package-global RNG; tests can only assert contract behavior, not exact placement.
