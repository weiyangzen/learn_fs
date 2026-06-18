<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nscd.c -->
# sources/user-network-fs/samba/source3/lib/util_nscd.c

## Purpose
`util_nscd.c` wraps optional NSCD cache flushing for passwd and group services.

## Important APIs, types, and functions
Public functions are `smb_nscd_flush_user_cache` and `smb_nscd_flush_group_cache`. Internal `smb_nscd_flush_cache` calls `nscd_flush_cache` only when build-time support exists.

## Control flow
User and group flush functions pass `"passwd"` or `"group"` to the internal helper. If `HAVE_NSCD_FLUSH_CACHE` is unavailable, the helper is a no-op. If flushing fails, it logs at debug level 10.

## State and persistence behavior
It affects external NSCD process caches when supported. Samba keeps no local state here.

## Dependencies and integration points
The file conditionally depends on `<libnscd.h>` and NSCD APIs. It is used after passwd/group changes so NSS cache data does not stay stale.

## Risks and edge cases
Failure logging is low severity because NSCD may not be running. Build configurations without NSCD support silently no-op.

## Test signals
Tests can compile both with and without NSCD support and mock flush failures to validate service names and logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nscd.c -->
