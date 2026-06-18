<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump.go -->
# sources/user-network-fs/rclone/fs/dump.go

## Purpose
Defines bit flags for rclone's `--dump` diagnostics.

## Important APIs, Types, And Control Flow
`DumpFlags` aliases generic `Bits[dumpChoices]`. Constants define headers, bodies, requests, responses, auth, filters, goroutines, open files, mapper, curl, errors, and trace. `dumpChoices.Choices` maps bits to CLI strings, `Type` returns `DumpFlags`, and `DumpFlagsList` is generated from help text.

## State And Persistence
Pure constants and generated help string.

## Dependencies And Integration Points
Consumed by HTTP dump/logging code, filter dump output, and global config options. Relies on generic bit flag parsing.

## Risks And Test Signals
Bit values are serialized and compatibility-sensitive. Tests cover string, set, type, and JSON behavior including unknown bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump.go -->
