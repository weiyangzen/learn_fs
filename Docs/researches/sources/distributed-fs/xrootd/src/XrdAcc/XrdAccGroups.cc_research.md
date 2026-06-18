# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.cc

## Purpose

`XrdAccGroups.cc` implements group and netgroup lookup support for authorization. It registers configured group names, resolves Unix group memberships and NIS netgroups, caches lookup results with TTLs, supports primary-only mode, and handles gid retranslation exceptions. The file was read completely.

## Important APIs, Types, and Functions

The global `XrdAccGroupMaster` is the process group helper. `AddName()` and `FindName()` manage interned group/netgroup names. `Groups()` returns relevant Unix groups for a user. `NetGroups()` returns configured netgroups matching user/host/domain. `PurgeCache()` clears both caches. `Retran()` configures gids that must be retranslated. Private `addGroup()` filters Unix groups to configured names. `Dotran()` suppresses cached group names for retran gids. External `XrdAccCheckNetGroup()` is applied across netgroup names.

## Control Flow

Configured auth DB records call `AddName()` to register names and mark whether Unix groups or netgroups are needed. `Groups()` first checks the TTL cache, then uses `XrdSysPwd`, primary gid, and optionally `getgrent()` to build a filtered list while holding `Group_Build_Context` around non-thread-safe group APIs. `NetGroups()` builds `user@host` cache keys, applies `innetgr()` to each configured netgroup, caches the result, and returns a copy.

## State and Persistence Behavior

State is in memory: registered group/netgroup name hashes, result caches, mutexes, retran gid list, NIS domain pointer, options, feature flags, and TTL. Caches are purged on authorization table swap. No durable group state is stored by this module.

## Dependencies and Integration Points

It depends on POSIX password/group APIs, `innetgr`, `XrdSysPwd`, `XrdOucHash`, `XrdAccGroups.hh`, and authorization config. MUSL builds stub `innetgr()` to always return false.

## Risks and Edge Cases

`XrdAccGroupList` construction in the header caps copy count to `NGROUPS_MAX` but uses the original `cnt` when zeroing the tail, which can write out of bounds if `cnt > NGROUPS_MAX`. `Retran()` checks `retrancnt > capacity`, allowing `retrancnt == capacity` to write one past the array. Cache entries store empty lists too, and callers receive null for no groups. Unix group enumeration is expensive and serialized. MUSL lacks netgroup support here.

## Test Signals

Tests should cover primary group only, supplementary groups, configured-name filtering, cache hits and purges, TTL expiry, `gidretran`, too many groups/netgroups, NIS domain behavior, MUSL netgroup stubbing, and boundary counts at `NGROUPS_MAX` and retran capacity.
