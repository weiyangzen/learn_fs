# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.hh

## Purpose

`XrdAccGroups.hh` declares group-list containers and the group/netgroup lookup manager used by authorization. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccGroupList` wraps up to `NGROUPS_MAX` group name pointers with `First()`, `Next()`, and `Reset()`. `XrdAccGroups_Options` defines `Primary_Only` and debug flags. `XrdAccGroupType` distinguishes Unix groups and netgroups. `XrdAccGroups` exposes domain, name registration/lookup, `Groups()`, `NetGroups()`, cache purge, gid retranslation, domain/lifetime/options setters, and constructor.

## Control Flow

`XrdAccConfig` registers group names while parsing DB records. `XrdAccAccess` calls `Groups()` and `NetGroups()` only when matching configured group or netgroup privileges.

## State and Persistence Behavior

`XrdAccGroups` owns in-memory name hashes and TTL caches protected by separate mutexes. It also stores up to 128 retran gids, domain, lifetime, options, and feature flags. The group list object stores pointers to interned names rather than owning strings.

## Dependencies and Integration Points

It depends on `<grp.h>`, platform `NGROUPS_MAX`, `XrdOucHash`, and pthread wrappers. It is used by `XrdAccConfig` and `XrdAccAccess`.

## Risks and Edge Cases

`XrdAccGroupList` copies at most `NGROUPS_MAX` entries but its zero-fill uses `cnt`, not the clamped count, if a larger count is supplied. Returned group names rely on interned-name lifetime. Cache validity depends on explicit purge and TTL.

## Test Signals

Tests should cover iteration, copy construction, empty lists, max-size lists, over-max inputs, cache option setters, and use with both Unix group and netgroup name tables.
