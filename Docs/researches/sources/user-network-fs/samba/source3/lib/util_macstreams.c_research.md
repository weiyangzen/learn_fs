<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.c -->
# sources/user-network-fs/samba/source3/lib/util_macstreams.c

## Purpose
`util_macstreams.c` identifies Apple AFP metadata/resource stream names.

## Important APIs, types, and functions
Public functions are `is_afpinfo_stream`, `is_afpresource_stream`, and `is_apple_stream`.

## Control flow
Each specific predicate null-checks the stream name and performs prefix comparison against `AFPINFO_STREAM_NAME` or `AFPRESOURCE_STREAM_NAME` using plain `strncasecmp`. `is_apple_stream` returns true if either specific predicate matches.

## State and persistence behavior
No state is kept. The functions are pure string predicates.

## Dependencies and integration points
It depends on `MacExtensions.h` constants and is used by VFS/streams code that treats Apple metadata streams specially.

## Risks and edge cases
The prefix comparison intentionally ignores multibyte string wrappers. Because it checks only the prefix length, callers must decide whether suffixes are acceptable for their stream syntax.

## Test signals
Tests should cover null input, exact AFP info/resource names, case-insensitive names, prefixed names, and non-Apple streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_macstreams.c -->
