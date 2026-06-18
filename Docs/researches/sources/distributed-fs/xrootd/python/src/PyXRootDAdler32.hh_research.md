# sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.hh

## Purpose
This header declares the Python C API entry point for the Adler-32 xattr helper.

## Important APIs, Types, and Functions
It declares `extern "C" PyObject* setXAttrAdler32_cpp(PyObject* self, PyObject* args)` in namespace `PyXRootD`.

## Control Flow
No runtime flow; it enables `PyXRootDModule.cc` to register the function implemented in `PyXRootDAdler32.cc`.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Depends on `Python.h`. Included by the module initializer and the implementation file.

## Risks and Test Signals
Risk is limited to signature mismatch between declaration, implementation, and module method table. Build and import tests cover it.
