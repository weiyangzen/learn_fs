# sources/user-network-fs/rclone/cmd/serve/docker/driver.go

## Purpose

`driver.go` implements the stateful Docker volume driver: volume registry, state persistence, mount monitoring, cache clearing, and lifecycle cleanup.

## Important APIs, Types, and Functions

`Driver` stores root path, volumes map, state path, mount/VFS defaults, synchronization, and monitor channels. Public methods are `NewDriver`, `Exit`, `Create`, `Remove`, `List`, `Get`, `Path`, `Mount`, and `Unmount`; internal helpers include `monitor`, `clearCache`, `getVolume`, `listVolumes`, `saveState`, and `restoreState`.

## Control Flow

Construction creates cache directories, copies defaults, optionally restores JSON state, starts a monitor goroutine, registers atexit unmounting, and notifies systemd. Driver API methods lock the mutex, mutate `volumes` and per-volume mount IDs, and save state after persistent changes. The monitor selects on control signals and mount error channels, clearing caches or cleaning up externally unmounted volumes.

## State and Persistence Behavior

State persists as JSON `docker-plugin.state` under rclone's cache dir. `Exit` unmounts all volumes and persists definitions without active mount IDs. In-memory state is guarded by `mu`.

## Dependencies and Integration Points

It depends on mountlib, VFS options, rclone config/cache directories, systemd daemon notifications, atexit hooks, and `Volume` setup/mount methods.

## Risks and Test Signals

The `monitor` function appears to build both `monChan` and `hupChan` select cases from `drv.monChan`, so SIGHUP cache clearing via `hupChan` may be unreachable. Other risks include state-file corruption handling, blocking sends to `monChan`, and holding `mu` during potentially slow mount operations. Tests cover driver CRUD, persistence, and mount reference counts.
