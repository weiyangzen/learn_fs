# sources/user-network-fs/rclone/backend/union/entry.go

Purpose: union-level `Object` and `Directory` wrappers that present the union `Fs` as parent while retaining all upstream candidate entries.

Important APIs: `Object`, `Directory`, internal `entry` interface, `Object.Update`, `Remove`, `SetModTime`, `Open`, tier/id/mime helpers, and directory `ModTime`, `Size`, `SetMetadata`, `SetModTime`.

Control flow/state: object mutations select candidates via action policy. If update candidates are all unwritable, update falls back to creating a new object and replacing wrapper state. Multi-upstream updates tee one reader through `multiReader`, write concurrently, drain failed branch readers, and aggregate `Errors`. `Open` serializes writeback, copies to configured writeback upstream if needed, appends the new candidate, then opens the selected object.

Dependencies/integration: union `upstream`, rclone `fs`, and helpers from `union.go`/`errors.go`.

Risks/test signals: partial fan-out failures, writeback candidate duplication, and aggregate directory metadata semantics. Internal RO tests validate write fallback behavior.
