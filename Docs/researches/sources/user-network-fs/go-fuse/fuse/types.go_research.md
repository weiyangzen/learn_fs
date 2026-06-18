# `sources/user-network-fs/go-fuse/fuse/types.go`

## Purpose
Declares the cross-platform FUSE wire structs, status constants, capability bits, request/response payload types, TTL helpers, caller identity, lock conversion helpers, and newer statx/copy-file-range structures.

## Important APIs, Types, And Functions
Important APIs include `Status`, errno constants, `SetAttrInCommon` getters, `InitIn/InitOut.Flags64`, `EntryOut`/`AttrOut` timeout helpers, `FileLock` conversion methods, `InHeader`, `OutHeader`, `ReadIn`, `WriteIn`, xattr, ioctl, notify, and statx structs.

## Control Flow
Handlers parse these structs from request buffers, fill output structs, then `request.serializeHeader` packages them for the kernel. Helper getters decode optional setattr fields based on `Valid` bits and produce Go `time.Time` values.

## State And Persistence
No active state is stored here; structs model kernel protocol state, TTLs, capabilities, inode ids, file handles, owners, and offsets.

## Dependencies And Integration Points
Depends on `syscall`, `time`, and `io`; platform files add OS-specific `Attr`, errno, and capability variants.

## Risks And Edge Cases
Wire compatibility is the main risk: field order, sizes, version-dependent flags, and errno aliases must match kernel/macFUSE/FreeBSD expectations. `SetAttrInCommon` uses current time for NOW flags, making tests time-sensitive.

## Test Signals
Type behavior is exercised by protocol parsing, print formatting tests, lock tests, setattr/fsetattr tests, and broad integration suites.
