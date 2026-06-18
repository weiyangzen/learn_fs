# sources/user-network-fs/nfs-utils/support/junction/path.c

## Purpose
Converts between FedFS/NSDB pathname component arrays and local POSIX path strings.

## Important APIs, Types, and Functions
`nsdb_free_string_array()`, `nsdb_path_array_to_posix()`, `nsdb_posix_to_path_array()`, plus helpers for normalization, component counting, zero-component allocation, XDR quad length, and UTF-8 validation placeholder.

## Control Flow
Array-to-POSIX validates each component, joins with slashes, normalizes duplicate/trailing slashes, and returns `/` for zero components. POSIX-to-array normalizes the input, counts components and encoded length, allocates a NULL-terminated array, and duplicates each component.

## State and Persistence Behavior
Returned path strings and arrays are heap-owned by callers. No persistent state.

## Dependencies and Integration Points
Used by libjunction public pathname conversion APIs and NFS location handling.

## Risks and Edge Cases
UTF-8 validation is a stub that always returns true. Component length checks mix NAME_MAX and 255 limits. Empty string normalization returns server fault rather than bad name.

## Test Signals
Test root path, repeated slashes, trailing slashes, empty input, too-long components, embedded slash in components, non-ASCII/invalid UTF-8 once implemented, and cleanup on allocation failure.
