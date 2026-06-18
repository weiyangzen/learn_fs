# sources/user-network-fs/rclone/vfs/vfscommon/cachemode.go

## Purpose
Defines the typed VFS cache-mode enum used by command-line flags, config, JSON, and VFS behavior selection.

## APIs, Flow, And State
`cacheModeChoices.Choices` maps enum values to `off`, `minimal`, `writes`, and `full`. `CacheMode` is an alias of rclone's generic `fs.Enum`, with constants ordered from least to most caching. `Type` returns `CacheMode` for flag reporting. There is no persistence beyond config serialization by the shared enum machinery.

## Dependencies And Integration
Depends on `github.com/rclone/rclone/fs`. `Options.CacheMode`, VFS open logic, tests, and mount flags use these values to choose cache semantics.

## Risks And Test Signals
The integer order is semantically important because tests and code compare modes with `<`. Adding a mode requires preserving ordering and updating tests/documentation. `cachemode_test.go` verifies string conversion, parsing, JSON unmarshalling, and invalid values.
