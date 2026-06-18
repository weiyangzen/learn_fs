# sources/user-network-fs/samba/source4/torture/raw/qfsinfo.c

## Purpose
This file implements `torture_raw_qfsinfo()`, a raw SMB filesystem-information suite. It probes many `RAW_QFS_*` levels and verifies that equivalent levels report consistent volume, allocation, device, attribute, quota, full-size, and string-encoding data.

## Important APIs, Types, And Functions
The static `levels[]` table maps human-readable names to `enum smb_fsinfo_level` values and stores capability masks, NTSTATUS results, and `union smb_fsinfo` output. `find()` returns a successful level by name. Local macros compare scalar, approximate scalar, string, structure, and unknown fields. The test uses `smb_raw_fsinfo()` to fetch all levels and `wire_bad_flags()` to validate returned string termination/encoding.

## Control Flow
`torture_raw_qfsinfo()` iterates through every table entry, sets `fsinfo.generic.level`, and calls `smb_raw_fsinfo()`. It then checks that all capability-advertised levels succeed, with `CAP_UNIX` gating the Unix level. After the status pass, it validates aliases such as `SIZE_INFO`/`SIZE_INFORMATION`, `DEVICE_INFO`/`DEVICE_INFORMATION`, `VOLUME_INFO`/`VOLUME_INFORMATION`, and `ATTRIBUTE_INFO`/`ATTRIBUTE_INFORMATION`.

The test compares disk size and free-space values between legacy `DSKATTR` and `ALLOCATION`, accepts approximately equal available units where live filesystems can change, checks `VOLUME` against `VOLUME_INFO`, checks `SIZE_INFO` against `FULL_SIZE_INFORMATION`, verifies quota/object-id unknown fields are zero when present, and finally checks correct string wire termination for volume and filesystem type fields.

## State And Persistence Behavior
The test creates no files and mutates no server state. It reads live filesystem state, so free-space-related values can change while the test is running. Like `qfileinfo.c`, it stores probe results in a static mutable `levels[]` table, making the implementation simple but not reentrant.

## Dependencies And Integration Points
Dependencies include `libcli` raw SMB APIs, the torture framework, NTSTATUS helpers, math functions for approximate size comparisons, negotiated capability flags, and Samba string wire helpers. The suite is registered by `raw.c` as the `qfsinfo` one-SMB test.

## Risks And Edge Cases
Some comparisons assume a mostly quiescent filesystem; concurrent allocation can affect available-space comparisons. The failure guard appears inverted: after counting failed levels it asserts `count > 13` with message "too many level failures", which is unusual and may be historical behavior worth reviewing before modifying. Optional or obsolete levels such as object-id information are guarded, and Unix info depends on negotiated capabilities.

## Test Signals
Success means all advertised query levels work and alias levels agree. Diagnostics identify failed levels, inconsistent disk sizes/free space, unexpected nonzero unknown fields, and string termination errors. The test also prints volume name, filesystem type, total disk, and free disk values as useful context.
