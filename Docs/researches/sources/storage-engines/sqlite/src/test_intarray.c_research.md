# sources/storage-engines/sqlite/src/test_intarray.c

## Purpose

`test_intarray.c` implements a test-only read-only virtual table over a C array of `sqlite3_int64` values, useful for testing `x IN intarray_name` without binding many separate parameters.

## Important APIs, types, and functions

`sqlite3_intarray` stores element count, element pointer, and destructor. `intarray_vtab` points at that object and `intarray_cursor` stores the current index. Public APIs are `sqlite3_intarray_create()` and `sqlite3_intarray_bind()`. Test Tcl commands expose both APIs through pointer strings.

## Control flow

Create allocates an intarray object, registers a per-object module named by the caller, then creates `temp.<name>`. Scans reset cursor index to zero, return `a[i]`, use `i` as rowid, advance by incrementing, and stop at `i >= n`. Binding frees the previous array through its destructor and installs the new pointer/count/destructor.

## State and persistence behavior

The TEMP virtual table exists for the connection lifetime or until DROP. The integer data is not copied; callers must keep it stable while queries run. Bound arrays are freed on rebind or object destruction if `xFree` is supplied.

## Dependencies and integration points

It depends on `test_intarray.h`, virtual table APIs, and Tcl test pointer helpers. It integrates with planner and expression tests for `IN` operator behavior and virtual table lifecycle.

## Risks and test signals

`xBestIndex` advertises no constraints, so scans are linear. Rebinding during active scans is undefined. Signals include query results matching bound values, empty initial tables, destructor execution on rebind/drop, and cleanup on connection close.
