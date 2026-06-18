# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.cc

## Purpose

`XrdAccAuthFile.cc` implements the default file-backed authorization database reader. It serializes access to an auth file, tokenizes records with `XrdOucStream`, reports parse errors, tracks modification time for warm refresh, and returns record components to `XrdAccConfig`. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccAuthDBObject()` returns a static `XrdAccAuthFile`. The constructor initializes state and an initial error context. `Open()` sets/uses the database path, stats and opens the file, records `st_mtime`, attaches the fd to `DBfile`, and locks `DBcontext`. `getRec()` returns record type/name. `getID()` reads selector type/value pairs. `getPP()` reads template names or path/privilege pairs. `Changed()` compares paths and mtimes. `Close()` closes the stream, unlocks, and returns parse success. `Bail()` centralizes open failure cleanup. `Copy()` bounded-copies stream words into stable buffers.

## Control Flow

The reader is opened under a mutex and remains locked for the full enumeration. `getRec()` skips invalid records and flushes unconsumed words from prior records. It accepts `g`, `h`, `s`, `n`, `o`, `r`, `t`, `u`, `x`, and `=` record types. `getPP()` treats non-slash words as templates, slash-starting words as paths needing a following privilege string, and backslash-prefixed words as escaped object ids.

## State and Persistence Behavior

State includes auth file path, flags, current record type, last modification time, `XrdOucStream`, mutex, and fixed buffers for record names and paths. Persistent source state is the auth file on disk; in-memory enumeration state is reset per open.

## Dependencies and Integration Points

It depends on `XrdOucStream`, POSIX `open/stat`, `XrdSysError`, and `XrdAccAuthDB`. `XrdAccConfig` consumes this implementation through the abstract factory.

## Risks and Edge Cases

If `Open()` is called with no configured path, it returns through `Bail()` and unlocks. Record and path buffers are bounded by `MAXHOSTNAMELEN` and `MAXPATHLEN`; long tokens are truncated silently by `Copy()`. `Changed()` returns unchanged when `stat()` fails after logging, which can delay recovery from file removal/recreation. Parse errors are accumulated in flags and only fail definitively at `Close()`.

## Test Signals

Tests should cover valid auth files, each record type, templates, escaped object IDs, missing privileges, invalid selectors, invalid record types, long tokens, path changes, mtime changes, missing files, and serialized concurrent opens.
