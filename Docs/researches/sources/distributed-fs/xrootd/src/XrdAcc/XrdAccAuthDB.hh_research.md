# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthDB.hh

## Purpose

`XrdAccAuthDB.hh` defines the abstract authorization database reader interface consumed by `XrdAccConfig`. The file was read completely.

## Important APIs, Types, and Functions

The abstract API is `Open()`, `getRec()`, `getID()`, `getPP()`, `Close()`, and `Changed()`. It also declares `XrdAccAuthDBObject()` as the factory returning the active database provider.

## Control Flow

Configuration opens the database, repeatedly calls `getRec()` for record type/name, then consumes either selector pairs via `getID()` or path/template/privilege entries via `getPP()`, and finally calls `Close()`. Warm refresh checks `Changed()` first.

## State and Persistence Behavior

The interface owns no state, but implementations are expected to serialize enumeration and track source modification state. The documented file syntax supports continuation records, comments, blank lines, typed id records, set definitions, templates, and path privilege pairs.

## Dependencies and Integration Points

It depends on `XrdSysError` for diagnostics. The default implementation is `XrdAccAuthFile`, but alternate database backends can implement the same stream-like contract.

## Risks and Edge Cases

The API returns pointers whose lifetime is implementation-defined, so `XrdAccConfig` must copy data when needed. The single-cursor style means concurrent use requires implementation-level locking. Malformed records must be surfaced through `Close()` returning false.

## Test Signals

Backend tests should cover normal enumeration, malformed records, changed/not-changed detection, missing database paths, continuation syntax, and concurrent open attempts.
