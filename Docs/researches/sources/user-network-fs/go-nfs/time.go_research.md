# sources/user-network-fs/go-nfs/time.go

## Purpose

`time.go` provides conversion helpers between Go `time.Time` values and the NFS wire time representation used by this package. It wraps seconds and nanoseconds into a simple `FileTime` struct equivalent to the client package's `NFS3Time`.

## Important APIs, Types, and Functions

`FileTime` has `Seconds uint32` and `Nseconds uint32`. `ToNFSTime(t time.Time)` converts a Go time to NFS seconds and nanoseconds. `FileTime.Native()` converts back to a `*time.Time`. `FileTime.EqualTimespec(sec, nsec)` compares against local stat-style second/nanosecond values.

## Control Flow

`ToNFSTime` calls `t.Unix()` and `t.UnixNano() % time.Second`. `Native` calls `time.Unix` with the stored values and returns the address of the local result. `EqualTimespec` casts input seconds and nanoseconds to `uint32` and compares both fields.

## State and Persistence Behavior

The file is stateless. Time values are copied into request/response structs and no global clock state is stored.

## Dependencies and Integration Points

It depends only on the standard `time` package. Attribute serialization and comparison code elsewhere in the NFS package can use `FileTime` when emitting NFS file attributes or applying setattr requests.

## Risks and Edge Cases

Seconds are truncated to 32 bits, so times beyond the NFSv3 unsigned 32-bit range wrap. Negative Unix times also wrap. The TODO in `EqualTimespec` notes missing overflow/bounds checks, and `ToNFSTime` can produce unexpected nanoseconds for pre-epoch times because Go's remainder keeps the sign of the dividend. Returning `*time.Time` from `Native` is safe but uncommon for a value conversion and may force allocation.

## Test Signals

Tests should cover round trips for ordinary times, zero time behavior, boundary seconds near `math.MaxUint32`, negative/pre-epoch times, nanosecond precision, and `EqualTimespec` overflow cases. Attribute-oriented NFS integration tests indirectly exercise this conversion when checking file metadata.
