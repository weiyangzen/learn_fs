<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_windows.go -->
# sources/user-network-fs/rclone/cmd/cmount/mountpoint_windows.go

## Purpose

`mountpoint_windows.go` handles Windows cmount path interpretation for drive-letter mounts, directory mounts, default drive selection, and UNC network-share presentation.

## Important APIs, Types, and Functions

Regex-backed helpers identify drive strings, drive roots, default markers, and network share paths. `getUnusedDrive` uses `file.FindUnusedDriveLetter`. `handleDefaultMountpath`, `handleNetworkShareMountpath`, `handleLocalMountpath`, and `handleVolumeName` normalize mountpoint and volume options. `getMountpoint` logs ignored Unix-only flags, routes the mount path to the right handler, updates network mode and volume prefix, and returns the WinFsp mountpoint.

## Control Flow

Default or `*` paths allocate a free drive. UNC paths force network mode and use the UNC as volume prefix. Local paths must not already exist; non-drive directory paths are made absolute and must have an existing parent.

## State and Persistence Behavior

The function reads local filesystem and drive state but does not create the mountpoint. It mutates `mountlib.Options` fields such as `NetworkMode` and `VolumeName`.

## Dependencies and Integration Points

It integrates with Windows cgofuse/WinFsp expectations, rclone `mountlib`, Fs overlap checks, and the local drive-letter utility.

## Risks and Test Signals

Risks include UNC parsing gaps, extended-length path rejection, unexpected option mutation, drive-letter races, parent directory checks, and network mode/volume prefix mismatches. Tests should cover each regex helper, default drive allocation failure, drive-root trimming, UNC volume handling, directory parent errors, and overlap rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_windows.go -->
