# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.cc

## Purpose

`XrdAccCapability.cc` implements path capability matching and named domain/template capability lists for the authorization engine. The file was read completely.

## Important APIs, Types, and Functions

The `XrdAccCapability(char*, XrdAccPrivCaps&)` constructor stores a path, hash, privilege masks, and optional `@=` substitution position. The template constructor is defined inline in the header. The destructor deletes the rest of a capability chain. `Privs()` walks a chain, follows template pointers, matches path prefixes or substituted prefixes, and ORs positive/negative masks into a caller-provided accumulator. `Subcomp()` performs `@=` substitution comparison. `XrdAccCapName::~XrdAccCapName()` deletes named lists. `XrdAccCapName::Find()` returns the capability list for the longest suffix-style domain/name match.

## Control Flow

Authorization calls `Privs()` on candidate capability lists. The first matching capability in a chain applies and returns success. Template capabilities delegate to their referenced capability list. Domain lists use `Find()` to compare configured suffix names against the end of the target name.

## State and Persistence Behavior

Capability state is immutable after construction: path string, path length/hash, privilege masks, substitution indices, next pointer, and optional template pointer. Named lists store name strings and capability-list ownership. All state is in memory and rebuilt on auth DB refresh.

## Dependencies and Integration Points

It depends on `XrdAccPrivs`, C string functions, and external `XrdOucHashVal2`. It is used by config table construction and access privilege accumulation.

## Risks and Edge Cases

The stored `pkey` is computed but not used in the observed matching path, leaving prefix checks string-based. `Privs()` stops after the first match in a chain, so ordering of configured path capabilities matters. `@=` substitution matching requires a prefix, inserted substitute, and tail; malformed or unexpected substitute values can deny intended access. Destructor chain ownership requires callers to detach before deleting subchains.

## Test Signals

Tests should cover exact prefix matches, non-matches, chain order, template delegation, positive/negative mask ORing, `@=` substitution, domain suffix lookup, and destructor behavior for multi-node chains.
