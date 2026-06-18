# sources/distributed-fs/xrootd/python/src/PyXRootD.hh

## Purpose
This common header provides Python C API setup and a convenience macro for releasing the GIL around blocking XrdCl calls.

## Important APIs, Types, and Functions
It defines `PY_SSIZE_T_CLEAN`, includes `Python.h`, `string`, and `structmember.h`, and defines `async(func)` as `Py_BEGIN_ALLOW_THREADS; func; Py_END_ALLOW_THREADS`.

## Control Flow
There is no runtime control flow in the header. The `async` macro wraps synchronous C++ calls so Python threads can run while XrdCl performs I/O.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Included by almost every PyXRootD binding source/header. It is the shared Python C API prelude for the extension.

## Risks and Test Signals
The macro name `async` conflicts with modern C++/Python terminology but is a preprocessor symbol in C++. Wrapped code must not touch Python objects while the GIL is released. Tests should include concurrent Python-thread smoke tests and builds across supported C++ standards/compilers.
