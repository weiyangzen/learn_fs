# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneBlacklist.java

## Purpose

`OzoneBlacklist` models configured blacklisted Ozone users and groups and provides denial checks for normal and read-only blacklist settings.

## Important APIs, Types, and Functions

Constructors create unmodifiable username/group sets. Static factories read `OZONE_BLACKLIST_USERS`, `OZONE_BLACKLIST_GROUPS`, `OZONE_READ_BLACKLIST_USERS`, and `OZONE_READ_BLACKLIST_GROUPS`. `isBlacklisted(UserGroupInformation)` checks short username and group intersection. `checkBlacklist` throws `AccessControlException` for blacklisted users. Setters allow replacing volatile user and group sets.

## Control Flow

Authorization code constructs a blacklist from configuration and calls `checkBlacklist` before allowing access. Collection parsing helpers support both full configuration and raw config-value strings.

## State and Persistence Behavior

State is in-memory only, with volatile user/group sets refreshed by setters. Persistent source is Ozone configuration.

## Dependencies and Integration Points

It mirrors `OzoneAdmins` behavior and integrates with Hadoop UGI, Guava set intersection, Ozone config keys, and server authorization code.

## Risks and Edge Cases

There is no wildcard handling; only explicit usernames/groups deny access. Group membership comparisons depend on UGI group freshness. Empty/null config yields empty immutable sets and no denial.

## Test Signals

Test user denial, group denial, nonblacklisted pass-through, null UGI pass-through, read blacklist config parsing, raw-value parsing, runtime setter replacement, and access exception text.
