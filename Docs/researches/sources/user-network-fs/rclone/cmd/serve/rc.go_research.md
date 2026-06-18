<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc.go -->
# sources/user-network-fs/rclone/cmd/serve/rc.go

Source read: complete file, 350 lines, 7986 bytes, sha256 `276cc9160b2a1be8870c194abb34169026ac416ecc42536b85a82514a82d0b86`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/rc.go_research.md`.

## Purpose
Implements the remote-control API for starting, stopping, listing, and enumerating `rclone serve` protocol servers at runtime.

## Important APIs, types, and functions
`Handle` is the protocol server contract. Internal `server` records id, address, rc params, handle, and serve error channel. `Fn` is the registration callback type. `AddRc`, `startRc`, `stopRc`, `serveTypesRc`, `listRc`, and `stopAll` implement rc paths `serve/start`, `serve/stop`, `serve/types`, `serve/list`, and `serve/stopall`.

## Control flow
`startRc` validates the requested type, obtains the Fs from params, copies global config and filters into a background context, creates the protocol server, starts `Serve` in a goroutine, waits briefly for startup failure, then stores it under a random type-prefixed id. Stop paths call `Shutdown`, wait for the serve goroutine, and remove entries.

## State and persistence behavior
State is the process-global `serveFns` registry and `servers` map protected by `serveMu`. Server params are stored for listing. No persistent state is written, but servers keep remote connections/listeners alive until stopped.

## Dependencies and integration points
Depends on `fs/rc`, `fs/filter`, `errcount`, and protocol packages that register via `AddRc` from their init functions.

## Risks and edge cases
Holding `serveMu` while waiting on shutdown/startup can serialize operations and can deadlock if a server callback re-enters serve rc. The 100 ms startup probe may miss late failures. IDs are random but not collision checked beyond map assignment.

## Test signals
`rc_test.go` tests missing types, start errors, immediate stops, start/stop/list/types/stopall behavior. `servetest.TestRc` exercises protocol-specific rc wiring with live TCP checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc.go -->
