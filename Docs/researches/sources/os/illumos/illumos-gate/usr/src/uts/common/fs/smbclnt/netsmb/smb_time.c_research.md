# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_time.c

## Scope

This file implements SMB time conversion helpers between NT time, Unix `timespec`, and old SMB server-local second values.

## APIs And Behavior

- `DIFF1970TO1601` is the seconds offset between the Unix epoch and NT epoch.
- `TEN_MIL` is the number of 100 ns NT time units per second.
- `smb_time_NT2local()` converts NT time to Unix seconds/nanoseconds, clamping pre-1970 values to zero.
- `smb_time_local2NT()` converts Unix time to NT time, preserving Unix time zero as NT time zero.
- `smb_time_local2server()` converts Unix time to old server seconds by subtracting a timezone offset in minutes, clamping underflow to zero.
- `smb_time_server2local()` converts old server seconds to Unix `timespec` by adding the timezone offset and zeroing nanoseconds.

## Dependencies

- Used by SMB file attribute encoding and decoding paths.
- Includes SMB connection and subr headers, but the implementation is self-contained arithmetic.

## Risks And Invariants

- NT time conversions are GMT-based and deliberately do not apply timezone offsets.
- Old dialect conversions use minute offsets and preserve server zero as local zero.
- Nanosecond precision is truncated to 100 ns units when converting to NT time.
