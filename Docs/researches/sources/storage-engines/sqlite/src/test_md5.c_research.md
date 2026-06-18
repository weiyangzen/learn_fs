# sources/storage-engines/sqlite/src/test_md5.c

## Purpose

`test_md5.c` provides MD5 hashing utilities for SQLite tests, exposing Tcl commands for strings/files and SQL aggregate `md5sum()`.

## Important APIs, types, and functions

`MD5Context` stores hash state, bit counters, and a 64-byte block. Core functions are `MD5Init()`, `MD5Update()`, `MD5Transform()`, `MD5Final()`, and `byteReverse()`. Converters are `MD5DigestToBase16()` and `MD5DigestToBase10x8()`. Tcl callbacks are `md5_cmd()` and `md5file_cmd()`. SQL callbacks are `md5step()` and `md5finalize()`, registered by `Md5_Register()`.

## Control flow

Tcl commands hash an input string or file slice and format the digest. `md5sum()` initializes aggregate context lazily, appends non-NULL argument text bytes for each row, then finalizes to hex. `Md5_Register()` also calls `sqlite3_overload_function()` for API coverage.

## State and persistence behavior

State is per command invocation or per aggregate context. File commands only read. No persistent database state is created beyond function registration.

## Dependencies and integration points

It depends on Tcl, stdio/string routines, and SQLite function APIs. `test_func.c` auto-registers it, making `md5sum()` broadly available to Tcl tests.

## Risks and test signals

This is test hashing, not security design. SQL aggregate text handling uses `strlen()`, so embedded NULs are not fully included. Signals are known digest outputs, `md5file` offset/amount stability, and `md5sum()` result stability across query plans.
