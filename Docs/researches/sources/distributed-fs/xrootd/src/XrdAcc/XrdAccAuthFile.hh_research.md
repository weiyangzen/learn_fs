# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.hh

## Purpose

`XrdAccAuthFile.hh` declares the file-backed implementation of `XrdAccAuthDB`. The file was read completely.

## Important APIs, Types, and Functions

Public overrides are `Open()`, `getRec()`, `getID()`, `getPP()`, `Close()`, and `Changed()`. Private helpers are `Bail()` and `Copy()`. `DBflags` tracks `inRec`, `isOpen`, and `dbError`.

## Control Flow

The class exposes a streaming reader contract: open the file, read one record at a time, read its selectors or path/priv entries, close and check whether parse errors occurred.

## State and Persistence Behavior

State includes the error route, flags, stream, auth filename, current record type, last mtime, mutex, record-name buffer, and path buffer. `DBcontext` serializes access across callers.

## Dependencies and Integration Points

It includes platform limits, networking constants for `MAXHOSTNAMELEN`, `XrdOucStream`, `XrdSysPthread`, and the abstract auth DB header. It is instantiated by the default factory in the `.cc`.

## Risks and Edge Cases

Fixed-size buffers constrain auth id and path lengths. The path buffer is reused for both path and id values, so callers must copy values before the next token call if they need persistence. `DBflags` is a plain enum used as bit flags and cast after bit operations.

## Test Signals

Compile tests should cover platform definitions of `MAXHOSTNAMELEN` and `MAXPATHLEN`. Runtime tests should validate flag transitions for successful and failed opens and parse failures.
