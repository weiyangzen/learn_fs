# sources/user-network-fs/rclone/fs/object/object_test.go

## Purpose
`object_test.go` validates the behavior of the synthetic object helpers in `fs/object/object.go`.

## Important APIs, types, and functions
Tests cover `NewStaticObjectInfo`, `StaticObjectInfo.Hash`, `MemoryFs` methods, `MemoryFs.Put`, `NewMemoryObject`, `WithMimeType`, `Content`, `Hash`, `SetModTime`, `Open`, `Update`, and `Remove`.

## Control flow
`TestStaticObject` checks default fs/hashes and explicit hash maps. `TestMemoryFs` checks fs metadata methods, unsupported list/object/mkdir/rmdir behavior, and Put creating hashable content. `TestMemoryObject` reads full and partial content through range/seek options, updates content with known sizes that do and do not fit existing capacity, tests unknown-size streaming and zero-size update, and confirms remove errors.

## State and persistence behavior
All state is in-memory byte slices and timestamps. Tests deliberately keep an old content slice to assert buffer reuse or replacement behavior.

## Dependencies and integration points
The tests use rclone `fs` open options and hash constants, plus standard `bytes`/`io`. They protect helpers used across many other tests, so regressions can cascade.

## Risks and edge cases
Range behavior around negative starts, overly large ends, and seek offsets is simplified but important for callers using memory objects as test doubles. Buffer reuse assertions depend on slice capacity and content mutation details.

## Test signals
Coverage is broad for the intended fake-object semantics: object info, hash support/unsupported errors, memory fs put, range and seek reads, modtime changes, efficient update reuse, unknown size handling, zero-length content, and unsupported deletion.

Source-read signal: reviewed complete local file (196 lines). Functions/methods observed: `TestStaticObject`, `TestMemoryFs`, `TestMemoryObject`.
