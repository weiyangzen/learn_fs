# sources/user-network-fs/nfs-utils/support/export/fsloc.c

## Purpose
Parses export `refer=` and `replicas=` location data into the `servers` structure expected by nfsd export cache writers.

## Important APIs, Types, and Functions
Public APIs are `replicas_lookup()` and `release_replicas()`. Helpers include `method_list()`, `parse_list()`, debug-only `method_stub()`, and `replicas_print()`.

## Control Flow
`replicas_lookup()` dispatches on `FSLOC_NONE`, `FSLOC_REFER`, `FSLOC_REPLICA`, and debug stub methods. List data is split on unescaped colons while respecting bracketed IPv6 literals, then each `path@host[+host]` entry becomes a `mount_point`; plus signs in host lists are translated to colon separators for kernel output.

## State and Persistence Behavior
The returned `servers` object owns heap-allocated `mount_point`, host, and path strings and records whether data is referral or replica. `release_replicas()` frees the whole tree. No persistent storage is used.

## Dependencies and Integration Points
Depends on `fsloc.h`, `exportfs.h`, allocation/string routines, and `xlog`. Export cache serialization consumes the returned structures when writing `fs_locations` information to nfsd.

## Risks and Edge Cases
Malformed entries are logged and skipped, so partial lists may be accepted. The parser is bounded by `FSLOC_MAX_LIST`. IPv6 bracket handling only protects list splitting, not full address validation.

## Test Signals
Test referral and replica lists, multiple hosts with plus separators, bracketed IPv6 addresses, missing `@`, relative paths, overlong lists, and release behavior under partial allocation failures.
