# sources/user-network-fs/rclone/vfs/vfscommon/filemode.go

## Purpose
Wraps `os.FileMode` in a flag/config-friendly type for VFS file, directory, link, and umask options.

## APIs, Flow, And State
`FileMode.String` formats permissions as octal, `Set` parses octal text, `Type` identifies the flag type, and `UnmarshalJSON` accepts either string or integer config through `fs.UnmarshalJSONFlag`. No mutable package state is held.

## Dependencies And Integration
Used by `Options` for `DirPerms`, `FilePerms`, `LinkPerms`, and `Umask`. Integrated with rclone's config and flag systems through `fs.Flagger` support.

## Risks And Test Signals
Misparsing modes can produce incorrect mounted permissions or accept invalid octal values. `filemode_test.go` verifies formatting, octal parsing, invalid decimal-like digits, and JSON string/integer handling.
