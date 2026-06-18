# sources/storage-engines/sqlite/src/test_func.c

## Purpose

`test_func.c` registers many SQLite test SQL functions and Tcl commands used to probe function registration, result destructors, auxdata, encodings, recursive SQL evaluation, record decoding, subtypes, bind-origin metadata, and FTS ranking.

## Important APIs, types, and functions

`registerTestFunctions()` installs `randstr`, destructor tests, `test_auxdata`, `test_error`, `test_eval`, `test_isolation`, `test_counter`, hex-to-UTF converters, `real2hex`, `test_decode`, `test_extract`, `test_zeroblob`, subtype/frombind helpers, and aggregate `test_agg_errmsg16`. Tcl commands are `autoinstall_test_functions`, `abuse_create_function`, and `install_fts3_rank_function`; `rankfunc()` consumes FTS `matchinfo()` blobs.

## Control flow

Initialization creates Tcl commands, initializes SQLite, and auto-registers this function set plus `Md5_Register()`. Scalar functions mostly wrap public SQLite APIs; record functions use internal varint and VDBE serial decoding; `test_eval()` prepares and steps SQL recursively; `abuse_create_function()` expects `SQLITE_MISUSE` from invalid registrations.

## State and persistence behavior

Registered functions are connection/process state through auto-extensions. Auxdata and counter state are per expression, while `test_destructor_count_var` is process-global and intentionally not thread-safe.

## Dependencies and integration points

It depends on `sqlite3.h`, Tcl, `sqliteInt.h`, `vdbeInt.h`, and `test_md5.c`. It is a core integration surface for SQLite Tcl tests of UDF APIs, encodings, VDBE record format, FTS3 ranking, subtype propagation, and error-code behavior.

## Risks and test signals

Several functions intentionally expose internal or unsafe behavior, including unchecked zeroblob sizes and malformed record decoding. Signals include destructor counts returning to zero, auxdata reuse strings, exact IEEE754 hex, expected misuse codes, subtype/frombind results, and FTS rank errors for malformed blobs.
