# sources/user-network-fs/rclone/cmd/mountlib/check_linux.go

Purpose: Linux-specific mountpoint readiness and emptiness checks using mountinfo.

Important APIs: `CheckMountEmpty`, `singleEntryFilter`, `CheckMountReady`, and `CanCheckMountReady = true`. `CheckMountEmpty` first verifies that the mountpoint is not already a mount, then falls back to directory emptiness.

Control flow: `CheckMountReady` opens mountinfo, filters for the exact mountpoint, and expects exactly one entry; errors distinguish not mounted, duplicate entries, and mountinfo parse/open failures.

State/persistence: read-only inspection of `/proc` mount state and mountpoint directory. Dependencies include `github.com/moby/sys/mountinfo` and shared `checkMountEmpty`. Risks include path normalization/mount namespace differences and transient mountinfo races during mount startup. Tests are mostly integration via mount daemon wait behavior.
