# sources/test-tools/strace/bundled/linux/include/uapi/linux/stat.h

## Purpose

Defines Linux file mode constants for non-glibc contexts and the `statx(2)` result ABI. strace uses it to decode `struct statx`, request/result masks, and file attribute flags.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It conditionally exports `S_IF*`, `S_IS*`, and permission bit macros. `struct statx_timestamp` carries seconds, nanoseconds, and reserved space. `struct statx` is a fixed 0x100-byte extensible structure with mask, block size, attributes, link/uid/gid/mode, inode, size, blocks, attribute mask, four timestamps, device ids, mount id, DIO alignment, subvolume id, atomic write bounds, DIO read alignment, and reserved expansion. `STATX_*` request/result bits include basic stats, birth time, mount id variants, DIO alignment, subvolume, write-atomic, and DIO-read alignment. `STATX_ATTR_*` flags describe compression, immutability, append-only, nodump, encryption, automount, mount root, verity, DAX, and atomic write support.

## Control Flow, State, and Integration

There is no local control flow. The syscall fills fields according to the requested mask and filesystem support; unavailable data may be fabricated or omitted as documented. State is filesystem metadata and mount/file attributes at the time of lookup.

## Risks and Test Signals

Risks include assuming requested bits are always returned, failing to parse newer fields after `stx_mnt_id`, treating `STATX_ALL` as future-complete, and confusing `stx_attributes` with `stx_attributes_mask`. Test signals include statx decode tests for partial masks, atomic write fields, DIO alignment, mount id unique, and all attribute flags.
