# sources/user-network-fs/rclone/vfs/vfscommon/filemode_test.go

## Purpose
Tests `FileMode` formatting, flag parsing, and JSON unmarshalling.

## APIs, Flow, And State
Interface assertions check `fs.Flagger` and non-pointer flag support. Table tests cover zero, standard permissions, high bits such as `02666`, invalid octal `999`, JSON strings, JSON integers, and expected resulting `FileMode` values.

## Dependencies And Integration
Uses `fs` flag interfaces and Go `encoding/json`. The tests support VFS option correctness for permission-related flags.

## Risks And Test Signals
Coverage is narrowly focused on serialization and parsing. It does not validate the later umask masking in `Options.Init`, but it catches the main user-facing parse errors.
