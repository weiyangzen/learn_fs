<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list.go -->
# sources/user-network-fs/rclone/fs/config_list.go

## Purpose
Defines reusable flag/config value types for comma-separated and space-separated string lists using CSV quoting rules.

## Important APIs, Types, And Control Flow
`CommaSepList` and `SpaceSepList` implement `String`, `Set`, `Type`, and `fmt.Scanner`. Shared `genericList` serializes through `csv.Writer` with configurable comma rune, parses one CSV record from bytes, strips line-number context from parse errors, and scans all remaining token text.

## State And Persistence
List values are in-memory slices. Empty input resets the list to nil. No persistence is performed directly; callers store string representations in flags/config.

## Dependencies And Integration Points
Used by flag wrappers, password-command config, and any option needing shell-like space lists with quotes. Depends on `encoding/csv`.

## Risks And Test Signals
CSV space-separated semantics are not shell parsing; backslashes and single quotes are literal in many cases. Tests document quoting behavior and invalid bare quotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list.go -->
