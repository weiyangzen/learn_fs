
# sources/user-network-fs/rclone/fstest/testserver/testserver.go

Purpose: package `testserver` bridges Go tests and shell init scripts that start local integration-test services.

Important APIs/types/functions: `findConfig` locates `fstest/testserver/init.d`; `cmdPath`, `hasStartCommand`, `run`, `envKey`, `start`, `stop`, `Start`, and `CleanupAll` implement lifecycle. `trackedServers` records servers started by the process for force cleanup.

Control flow: `Start(remote)` parses the rclone remote, skips local/unconfigured names, locates script directory once, skips remotes with no script, runs `<script> start`, parses `key=value` output into `RCLONE_CONFIG_<REMOTE>_<KEY>` env vars, optionally probes `_connect` with retries and `_connect_delay`, tracks the server, and returns an idempotent stop closure. `CleanupAll` force-stops all still-tracked servers.

State/persistence: mutates process environment and in-memory tracked refcounts. Shell scripts manage external containers/processes and runtime state.

Dependencies/integration: uses `fspath.Parse`, rclone logging, Go networking, and all `init.d` scripts with the shared `run.bash` contract.

Risks: environment variables are process-global and can leak across tests. `_connect` only verifies TCP-level readiness. If script output includes unexpected lines, they are ignored unless matching key/value.

Test signals: start failures surface as Go errors; cleanup logging reports force-stop failures.
