# sources/sync-backup/syncthing/lib/testutil/testutil.go

Purpose: small reusable test I/O helpers.

Important APIs and control flow: `ErrClosed` marks closed blocking readers/writers. `BlockingRW` has a `done` channel; `Read` and `Write` block until `Close` closes `done`, then return `ErrClosed`. `Close` closes `done` idempotently through channel close semantics only if called once. `NoopRW` implements `Read` as immediate EOF and `Write` as accepting all bytes. `NoopCloser` implements no-op `Close`.

State and persistence: in-memory channel state only.

Dependencies and integration: test packages can use these to simulate blocked connections or harmless read/write endpoints.

Risks: `BlockingRW.Close` will panic if called more than once because it closes an already-closed channel. It is a test helper, so callers must coordinate close ownership. No tests in this subset.
