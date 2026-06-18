# sources/sync-backup/restic/cmd/restic/cmd_mount.go

Purpose: implements FUSE-backed `restic mount` on darwin/freebsd/linux, exposing snapshots read-only at a mountpoint.

Important APIs/types/functions: `registerMountCommand`; `MountOptions`; `runMount`; `validateMountpoint`; `checkMountpointOverlap`; `resolvePath`; `isInside`.

Control flow and state: validates time template and mountpoint argument, checks mountpoint existence, write/execute access, and local repository overlap. It opens a read lock, loads the index, creates read-only FUSE mount options including allow-other/default-permissions flags, constructs `fuse.NewRoot`, preloads snapshots via `ReadDirAll`, starts `fs.Serve` in a goroutine, and waits for context cancellation or serve completion. On cancellation it attempts unmount and returns `ErrOK`. No repository mutation occurs.

Dependencies and integration points: uses `github.com/anacrolix/fuse`, restic `internal/fuse`, local backend location parsing, unix access checks, snapshot filters, and debug logging.

Risks: FUSE lifecycle and unmount behavior are OS-sensitive. Overlap checks are critical to avoid deadlocks when mounting over/under a local repository. Path-template/time-template changes affect virtual directory layout.

Test signals: mount integration tests cover snapshot visibility, same-timestamp disambiguation, and overlap/symlink overlap detection.
