# sources/user-network-fs/rclone/vfs/vfscommon/cachemode_test.go

## Purpose
Tests the `CacheMode` enum's flag and JSON behavior.

## APIs, Flow, And State
Compile-time assertions ensure `*CacheMode` implements `pflag.Value` and `json.Unmarshaler`. Tests verify string names for known and unknown values, parsing of valid and invalid strings, `Type`, JSON string unmarshalling, numeric unmarshalling, and rejection of out-of-range numbers.

## Dependencies And Integration
Uses the generic `fs.Enum` behavior indirectly through `CacheMode`. These tests protect command-line and config compatibility for VFS cache modes.

## Risks And Test Signals
The tests catch broken enum mappings and invalid-value handling. They do not exercise VFS behavior per mode; that is covered in the functional `vfstest` suite.
