# sources/user-network-fs/rclone/fs/rc/registry.go

## Purpose
This file defines the registry for remote-control calls and the metadata used to expose them.

## Important APIs, Types, and Functions
- `type Func func(ctx context.Context, in Params) (out Params, err error)` is the RC handler signature.
- `type Call` stores path, function, title, auth metadata, help text, and whether the handler needs raw request/response interfaces.
- `Registry` stores path-to-call mappings under an RW mutex.
- `NewRegistry`, `(*Registry).Add`, `Get`, and `List` manage entries.
- `var Calls` is the global registry; `Add` is its package-level registration helper.

## Control Flow
Packages register calls in `init` via `rc.Add`. `Add` trims path slashes and help whitespace before storing the call. `List` snapshots keys, sorts them alphabetically, and returns calls in stable order.

## State and Persistence
The global `Calls` registry is process-wide mutable state. There is no disk persistence. Registered functions are stored as function pointers and omitted from JSON through the struct tag.

## Dependencies and Integration Points
The registry is used by `rcserver.handlePost`, `rc/js/main.go`, sync RC registration, WebGUI plugin registration, and other rclone packages that expose RC endpoints.

## Risks and Edge Cases
Duplicate paths overwrite previous calls without warning. Path normalization only trims leading/trailing slashes; internal path conventions are caller-owned. Global registration order can affect duplicate conflicts, though `List` output is deterministic.

## Test Signals
No dedicated tests in this subset target the registry directly, but server, sync RC, WebGUI RC, and WASM behavior all depend on `rc.Calls.Get`.
