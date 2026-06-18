# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.hh

## Purpose

`XrdAccCapability.hh` declares capability chains and named capability lists used by XRootD authorization tables. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccCapability` exposes `Add()`, `Next()`, three `Privs()` overloads, `Subcomp()`, a concrete path/privilege constructor, a template-reference constructor, and a destructor. `XrdAccCapName` maps a name/domain suffix to a capability list with `Add()` and `Find()`.

## Control Flow

Configured records become chains of capabilities. At access time, the authorization engine calls `Privs()` with a path and optional substitution string to merge privileges from the first matching capability or template.

## State and Persistence Behavior

Each capability owns either a concrete path/privilege record or a template pointer. Chain ownership is intrusive through `next`; deleting a node deletes all following nodes. `XrdAccCapName` similarly owns a linked list and the capability lists associated with names.

## Dependencies and Integration Points

It depends on `XrdAccPrivs.hh` and C string allocation. The config loader creates these objects, and `XrdAccAccess` consumes them.

## Risks and Edge Cases

Manual ownership and chain deletion are the main risks. `pathsub` support adds matching complexity. Because matching is prefix-based, configuration must distinguish file and directory path prefixes carefully.

## Test Signals

Tests should validate all constructors, list addition, suffix-name lookup, path prefix matching, substitution matching, and deletion without leaks or double frees.
