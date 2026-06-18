# File Research: sources/os/bsd/netbsd-src/lib/libutil/opendisk.c

## Purpose
Opens disk device paths using NetBSD raw/cooked naming conventions.

## Key Details
- Rejects `NULL` output buffer and `O_CREAT`.
- Gets raw partition number from `getrawpartition`.
- For plain disk names, tries `/dev/<r?>name`, then `/dev/<r?>name<rawpart>`.
- For paths with slashes, tries the path directly, then with raw partition letter appended.
- `opendisk1` accepts an injected open-like function.

## Dependencies and Role
- Core helper for disk and filesystem tools that need robust device-node discovery.
