# sources/user-network-fs/rclone/lib/kv/types.go

Source read signal: reviewed complete local file (34 lines, sha256 0ce0aad1c03bca0a).

Purpose: Defines the platform-independent KV abstraction and shared errors.

Important APIs/types/functions: Errors `ErrEmpty`, `ErrInactive`, `ErrUnsupported`; interfaces `Op`, `Bucket`, and `Cursor`.

Control flow: No runtime flow. `Op.Do` receives a context and abstract bucket; bucket/cursor interfaces mirror bbolt operations needed by callers.

State and persistence behavior: No state. Implementations provide persistence or unsupported stubs.

Dependencies and integration points: Uses `context` and `errors`. Both `bolt.go` and `unsupported.go` depend on these definitions, as do callers implementing KV operations.

Risks and test signals: Interface shape is effectively an internal ABI. `Bucket.Get` returns byte slices whose ownership follows backend semantics, so callers must copy if they retain data after transactions.
