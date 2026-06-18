# sources/storage-engines/sqlite/src/test_intarray.h

## Purpose

`test_intarray.h` declares the C API for the test-only intarray virtual table implemented in `test_intarray.c` and documents its intended use as a C-array backed SQL source.

## Important APIs, types, and functions

It declares opaque `sqlite3_intarray`, `sqlite3_intarray_create(sqlite3*, const char*, sqlite3_intarray**)`, and `sqlite3_intarray_bind(sqlite3_intarray*, int, sqlite3_int64*, void(*)(void*))`. The header has an include guard and C++ `extern "C"` block.

## Control flow

The documented lifecycle is create a named TEMP intarray table, prepare SQL referencing that name, bind or rebind arrays between executions, and let DROP or connection close destroy the object.

## State and persistence behavior

The API exposes process memory through a TEMP virtual table. Bind does not copy elements; array stability is the caller's responsibility. Optional `xFree` controls disposal of the bound array.

## Dependencies and integration points

It includes `sqlite3.h` and is consumed by the implementation and C tests. Comments explicitly steer production users to the `carray` extension instead.

## Risks and test signals

Do not create the same name twice on one connection and do not mutate/free bound arrays during active queries. Signals are compile-time API availability, C++ compatibility, and runtime SQL visibility through the paired implementation.
