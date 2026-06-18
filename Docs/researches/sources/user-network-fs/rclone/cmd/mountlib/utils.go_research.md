# sources/user-network-fs/rclone/cmd/mountlib/utils.go

Purpose: shared mount utility helpers for capacity clipping, local path overlap checks, non-empty mountpoint enforcement, and default volume/device names.

Important APIs: `ClipBlocks`, `CheckOverlap`, `absPath`, `CheckAllowNonEmpty`, `checkMountEmpty`, `MountPoint.SetVolumeName`, `Options.SetVolumeName`, and `MountPoint.SetDeviceName`.

Control flow: `CheckOverlap` only applies to local-like remotes, normalizes symlinks/absolute paths/trailing slashes, and rejects either path being a prefix of the other. `checkMountEmpty` opens the mountpoint and attempts one directory read. Name setters default to `fs.ConfigString`, sanitize `:` and `/`, and truncate Windows volume names.

State/persistence: read-only path inspection; mutates option fields. Dependencies include filesystem path APIs and rclone `fs`. Risks include prefix-based overlap false positives for edge path normalization, mountpoint directory read permissions, and platform-specific volume limits. Coverage is indirect via mount tests.
