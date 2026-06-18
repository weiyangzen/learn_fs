# sources/user-network-fs/rclone/fs/rc/rc.go

## Purpose
This file declares the remote-control global option schema, the runtime `Options` struct, and JSON response writer helper for the RC subsystem.

## Important APIs, Types, and Functions
- `OptionsInfo` is an `fs.Options` block containing RC, WebGUI, metrics, job expiry, auth, HTTP, and template options.
- `type Options` stores RC server, auth, WebGUI, metrics, and job expiration settings with `config` tags.
- `var Opt Options` holds global defaults loaded by the fs global option registry.
- `WriteJSON(w io.Writer, out Params) error` writes indented JSON responses.

## Control Flow
At init time, `fs.RegisterGlobalOptions` registers the `rc` option block and points it at `Opt`. `OptionsInfo` composes RC-specific options with prefixed HTTP/auth/template option groups, then sets defaults such as `localhost:5572` for RC and an empty metrics listener.

## State and Persistence
`Opt` is process-global mutable configuration populated through rclone's option machinery. This file itself does not persist to disk; persistence comes from config/env/flags handled by the broader fs config system.

## Dependencies and Integration Points
The file depends on `fs.Options`, `fs.Duration`, and `lib/http` configuration blocks. `rcserver.Start`, `MetricsStart`, `webgui`, and `jobs` consume `Options` at runtime.

## Risks and Edge Cases
Because `Opt` is global, tests and initialization code that mutate it can affect later behavior unless isolated. `WriteJSON` uses tab-indented JSON, which tests assert and clients may observe.

## Test Signals
`rc_test.go` directly verifies `WriteJSON` formatting. Option registration is exercised indirectly across server, flags, and integration tests.
