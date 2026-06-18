# sources/user-network-fs/mergerfs/src/stat_util.hpp

## Purpose
Provides tiny predicates around POSIX `struct stat`.

## Important APIs, Types, and Functions
`StatUtil::empty()` checks `st_size == 0`; `writable()` checks any user/group/other write bit; `writable_or_not_empty()` combines writable or non-empty.

## Control Flow
All helpers are inline boolean evaluations.

## State and Persistence Behavior
No state is retained and no filesystem changes occur.

## Dependencies and Integration Points
Includes `<sys/stat.h>` and can be used by filesystem operation filters, symlinkification, or cleanup code.

## Risks and Edge Cases
Permission-bit checks do not account for ACLs, capabilities, mount flags, or effective user identity.

## Test Signals
Unit tests should cover regular files, directories, zero-size files, write-bit combinations, and ACL/mount behavior at integration level.
