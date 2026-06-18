# sources/user-network-fs/rclone/vfs/vfsflags/vfsflags.go

## Purpose
Registers VFS command-line flags on a provided `pflag.FlagSet`.

## APIs, Flow, And State
`AddFlags` delegates to `flags.AddFlagsFromOptions` with `vfscommon.OptionsInfo`. It has no own state; it projects the shared option schema into CLI flags.

## Dependencies And Integration
Depends on rclone's config flag helper, `vfscommon`, and `spf13/pflag`. Mount commands call this package to expose VFS options.

## Risks And Test Signals
The file is thin, so risks are mostly drift in `OptionsInfo` or wrong prefix use. CLI/config integration tests elsewhere are the meaningful signal.
