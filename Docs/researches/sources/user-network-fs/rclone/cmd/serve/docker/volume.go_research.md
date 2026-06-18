# sources/user-network-fs/rclone/cmd/serve/docker/volume.go

## Purpose

`volume.go` defines Docker volume state and implements setup, validation, mount reference counting, unmounting, removal, and VFS cache clearing.

## Important APIs, Types, and Functions

Types include `Volume`, `VolOpts`, and `VolInfo`. Functions/methods include `newVolume`, `getInfo`, `prepareState`, `restoreState`, `validate`, `checkMountpoint`, `setup`, `remove`, `clearCache`, `mount`, `unmount`, and `unmountAll`. Errors include `ErrVolumeNotFound`, `ErrVolumeExists`, and `ErrMountpointExists`.

## Control Flow

New volumes choose a mountpoint under the driver root, apply options, verify/create an empty mountpoint, resolve a mount method, optionally create a persistent remote, and create an rclone Fs. Mount requests reject duplicate IDs, mount once for the first active ID, then record additional IDs as references. Unmount removes one ID and only performs real unmount on the last reference.

## State and Persistence Behavior

Public fields are serialized into driver JSON state. `Mounts` is regenerated from `mountReqs` before saving. Active mount internals, VFS handles, and driver pointers are runtime-only.

## Dependencies and Integration Points

It integrates rclone mountlib, VFS cache, backend creation, config remote creation/deletion, Docker mountpoint conventions, and platform mountpoint checks.

## Risks and Test Signals

Risks include mountpoint race/non-empty checks, persisted sensitive options, incomplete cleanup after partial setup, deleting persistent remotes, and Windows parent-dir behavior. Tests cover validation, mount references, state restore, and API remove-in-use behavior.
