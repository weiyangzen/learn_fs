# sources/sync-backup/syncthing/lib/rc/rc.go

## Purpose
Remote-control test utility for launching and controlling a Syncthing process through its REST API, tracking startup and synchronization state from events, and inspecting process logs for panics or data races.

## Important APIs, Types, and Functions
`Process` stores API address, device ID, folders, event-derived sequence/done maps, process command, log file, and lifecycle channels. Public methods include `NewProcess`, `ID`, `LogTo`, `Start`, `AwaitStartup`, `Stop`, `Stopped`, `Get`, `Post`, `Events`, rescan helpers, config helpers, pause/resume helpers, `Model`, `Connections`, `SystemStatus`, `SystemVersion`, and `RemoteInSync`. Package helpers `InSync` and `AwaitSync` compare event-derived sequence state across processes. `checkForProblems`, `eventLoop`, and `updateSequenceLocked` implement internal monitoring.

## Control Flow
`Start` launches the binary with `STNORESTART=1` and a fixed GUI API key, then starts `eventLoop` and `wait` goroutines. `eventLoop` polls `/rest/events`, loads config on `Starting`, tracks folders until all become idle, and updates local/remote sequence maps and done flags on index, summary, and completion events. REST helper methods build HTTP requests with the API key and parse JSON into typed structs. `Stop` requests `/rest/system/shutdown`, waits for process exit, and returns log-detected problems.

## State and Persistence Behavior
Persistent effects are external: it starts a Syncthing process, can write a log file via `LogTo`, posts config changes and scan requests, and shuts the process down. Internal state is protected by `eventMut` for sequence and done maps. `checkForProblems` reads the process log after exit and prints race or panic excerpts.

## Dependencies and Integration Points
Depends on `net/http`, `os/exec`, config loading, event types, model completion structs, `dialer.DialContext`, and `protocol.DeviceID`. It is integration-test infrastructure around Syncthing's REST endpoints: `/rest/events`, `/rest/db/scan`, `/rest/system/config`, `/rest/system/pause`, `/rest/system/resume`, `/rest/db/status`, `/rest/system/connections`, `/rest/system/status`, `/rest/system/version`, and `/rest/db/completion`.

## Risks and Edge Cases
The fixed API key is suitable for controlled test processes but not production secret management. Event polling assumes ordered event IDs and panics if `StateChanged` arrives before folders are loaded. `InSync` locks all processes in argument order; callers should pass stable ordering to avoid lock-order issues with other code. Startup waits depend on folder idle events, so missed events or API startup delays can hang higher-level tests. Log scanning uses textual heuristics for races and panics.

## Test Signals
There are no direct tests in this subset. Downstream integration tests validate that processes start, reach startup completion, synchronize sequences, expose REST status/config correctly, and report log problems on stop.
