<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc_test.go -->
# sources/user-network-fs/rclone/cmd/serve/rc_test.go

Source read: complete file, 180 lines, 4456 bytes, sha256 `98bafb04e516b30c85a7c7049a9ca73c4ccc039de241b516cc818c0cc0f22cc1`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/rc_test.go_research.md`.

## Purpose
Unit-tests the serve rc lifecycle manager using dummy server handles.

## Important APIs, types, and functions
`dummyServer` implements `Handle`. Test helper `newServer` variants simulate normal serve, construction failure, and immediate stop. `resetGlobals` and `newTest` isolate global registries.

## Control flow
Tests register a fake serve type, invoke rc functions directly with `rc.Params`, then inspect outputs, server map contents, and shutdown behavior.

## State and persistence behavior
Mutates the package-global `serveFns` and `servers` maps but resets them around each test. Dummy servers model listener address and error-channel lifetimes without opening sockets.

## Dependencies and integration points
Depends on rc params, net address behavior, and testify-style stdlib testing assertions.

## Risks and edge cases
Because tests are white-box and global-state based, parallelization would be unsafe unless isolation changes. They do not exercise real protocol listeners.

## Test signals
Covers unknown serve type, factory error, immediate stop error path, normal start/stop, nonexistent stop, sorted type/list output, and stopall cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc_test.go -->
