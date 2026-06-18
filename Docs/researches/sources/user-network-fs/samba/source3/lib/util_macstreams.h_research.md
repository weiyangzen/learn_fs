<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.h -->
# sources/user-network-fs/samba/source3/lib/util_macstreams.h

## Purpose
This header declares Apple stream classification helpers.

## Important APIs, types, and functions
It exposes `is_afpinfo_stream`, `is_afpresource_stream`, and `is_apple_stream`.

## Control flow
Consumers call the specific predicates or the aggregate predicate when handling named streams.

## State and persistence behavior
The header has no state.

## Dependencies and integration points
It provides a narrow API for VFS and SMB stream handling code without exposing `MacExtensions.h` details.

## Risks and edge cases
The implementation's prefix semantics should be understood by callers that require exact stream-name matching.

## Test signals
Compile coverage and the string predicate tests described for `util_macstreams.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.h -->
