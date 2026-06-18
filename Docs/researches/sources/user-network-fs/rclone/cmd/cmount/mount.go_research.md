<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount.go

## Purpose

`mount.go` registers and runs the cgo/cgofuse-based rclone mount implementation for supported cmount builds.

## Important APIs, Types, and Functions

`init` selects command naming (`cmount` on linux, `mount` plus `cmount` alias elsewhere), registers the mount command and rc mount handler, and appends a build tag. `mountOptions` translates `mountlib.Options` and VFS settings into cgofuse/WinFsp options. `waitFor` polls for readiness. `mount` resolves the mountpoint, creates `FS` and `fuse.FileSystemHost`, sets capabilities, starts `host.Mount` in a goroutine, builds an unmount closure, waits for `FS.Init`, and returns the error channel, unmount function, and mountpoint.

## Control Flow

Startup is asynchronous but the function waits until FUSE calls `Init` or mount exits early. Unmount shuts down VFS, avoids redundant host unmount after signals or destroy, and waits for Windows mountpoint disappearance.

## State and Persistence Behavior

It creates a live kernel/user-space mount and runtime VFS state. It may expose remote mutations through mounted filesystem operations but does not write config.

## Dependencies and Integration Points

It integrates `mountlib`, `vfs`, `atexit`, build info, cgofuse, OS runtime checks, and platform mountpoint helpers.

## Risks and Test Signals

Risks include platform option drift, early mount failure races, panic handling around missing WinFsp, unmount hangs, capability mismatch, and read-only option propagation. Tests should cover mount option construction per OS, early error paths, unmount closure behavior, Windows wait loops, signal handling, and VFS integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount.go -->
