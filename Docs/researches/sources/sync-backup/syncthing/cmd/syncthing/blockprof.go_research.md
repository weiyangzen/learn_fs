# sources/sync-backup/syncthing/cmd/syncthing/blockprof.go

Purpose: optional debug support for periodically writing Go block profiles from the Syncthing process.

Important APIs/functions: `startBlockProfiler` and `saveBlockingProfiles`.

Control flow: `startBlockProfiler` looks up the `block` profile, enables a goroutine, and panics if profile saving returns. `saveBlockingProfiles` sets block profile rate to 1 and every 20 seconds writes `block-<pid>-<ms>.pprof` based on elapsed runtime.

State and persistence: writes profile files to the current working directory. It changes global runtime block profiling rate.

Dependencies/integration: enabled from `serveCmd.syncthingMain` when `--debug-profile-block`/`STBLOCKPROFILE` is set.

Risks and test signals: aggressive block profiling can affect performance and produce unbounded files. No tests cover profile writing failure or cleanup.
