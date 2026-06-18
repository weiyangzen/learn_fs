# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.hh

## Purpose

`XrdAccConfig.hh` declares the authorization configuration singleton type and helper structures used to build access tables from config and auth DB sources. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccGlist` is a simple linked list of group names. `XrdAccConfig` exposes `Configure()`, `ConfigDB()`, public `Authorization`, `GroupMaster`, and `AuthRT`. Private helpers cover group list addition, DB record parsing, defaults, config-file execution, set id validation/definition, space substitution, privilege conversion, and directive handlers.

## Control Flow

The public flow is `Configure()` at startup and `ConfigDB()` during refresh. Private directive handlers mutate config options before DB load.

## State and Persistence Behavior

The class owns the database provider pointer, auth DB path, config mutex/thread wrapper, options, current rule number, space encoding char, and URI-path flag. Destructor frees `dbpath`.

## Dependencies and Integration Points

It depends on access, auth DB, capability, groups, `XrdOucStream`, `XrdOuca2x`, `XrdOucHash`, `XrdSysError`, and pthread wrappers. `XrdAccAccess` uses this singleton indirectly through the external `XrdAccConfiguration`.

## Risks and Edge Cases

The singleton design means only one authorization configuration can exist per process. Manual ownership of `dbpath`, capabilities, and hash tables requires care in refresh paths. Private friend-like coupling with `XrdAccAccess` is strong.

## Test Signals

Compile tests should cover all private handler declarations with implementation signatures. Functional tests should validate object construction defaults and repeated configuration/refresh behavior.
