# sources/storage-engines/wiredtiger/lang/python/CMakeLists.txt

## Purpose
This CMake file builds the WiredTiger Python API through SWIG, links it to a PIC-capable WiredTiger library, arranges the package layout, and defines a Python smoke test.

## Important APIs, Types, and Functions
It selects `wiredtiger_static` when `ENABLE_STATIC` and `WITH_PIC` are set, otherwise `wiredtiger_shared` when available, and fails if neither can support Python. It configures SWIG flags for Python 3, threads, optimization, no default constructors/destructors, generated include paths, and fixed interface name `_wiredtiger`. `swig_add_library` creates `wiredtiger_python`.

## Control Flow
Configuration chooses the link target, assembles SWIG/compiler warning flags per compiler family, declares the SWIG module, links against WiredTiger and `Python3::Python`, copies the Python package directory into the binary tree, post-build copies `init.py` to `__init__.py` and generated `wiredtiger.py` to `swig_wiredtiger.py`, fixes the output name, applies Darwin suffix handling, and adds a dependency on `wiredtiger_ext`.

## State and Persistence Behavior
The file creates build-tree package files and a shared extension module. Its post-build copies determine import-time package shape.

## Dependencies and Integration Points
It depends on CMake SWIG support, Python3, WiredTiger static/shared targets, generated headers/config, and `wiredtiger_ext`. The POSIX smoke test runs `examples/python/ex_access.py` with `PYTHONPATH` set to the binary package.

## Risks and Edge Cases
The Python API requires a shared or PIC static WiredTiger build. Generated module names are tightly coupled to `init.py`. Compiler warning suppressions may drift. Darwin uses `.so` suffix because Python dynamic module loading differs from normal shared libraries.

## Test Signals
`test_ex_access`, importability of `_wiredtiger`, and presence of `wiredtiger/__init__.py` and `wiredtiger/swig_wiredtiger.py` are the key signals.
