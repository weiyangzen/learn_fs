<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filterflags/filterflags.go -->
# sources/user-network-fs/rclone/fs/filter/filterflags/filterflags.go

## Purpose
Small adapter that registers filter options as command-line flags.

## Important APIs, Types, And Control Flow
`AddFlags` calls `flags.AddFlagsFromOptions(flagSet, "", filter.OptionsInfo)`, letting the generic config flag layer create all filter flags without backend prefixes.

## State And Persistence
Mutates the provided pflag set; no persistence.

## Dependencies And Integration Points
Connects `fs/filter.OptionsInfo` to `fs/config/flags` and command initialization.

## Risks And Test Signals
Behavior depends entirely on `OptionsInfo` and `AddFlagsFromOptions`. No direct tests; command flag registration and filter tests provide indirect signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filterflags/filterflags.go -->
