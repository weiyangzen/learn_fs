# sources/storage-engines/wiredtiger/bench/workgen/workgen/__init__.py

## Purpose
This package initializer makes the generated workgen extension modules look like one Python namespace. It appends the package directory to `sys.path`, imports `workgen` and `workgen_util`, and copies symbols from imported module objects into the package module.

## Important APIs, Types, and Functions
There are no declared functions or classes. The important state is `me = sys.modules[__name__]`, followed by dynamic `setattr(me, name, value)` for every symbol found in each imported module.

## Control Flow
On import, Python executes the file once, mutates `sys.path`, imports SWIG-generated support modules, iterates over `workgen`, then re-exports each discovered attribute into the package namespace. Runner scripts can then use `from workgen import *` without knowing the generated module layout.

## State and Persistence Behavior
The file mutates process-global import state by appending the package directory to `sys.path`. It also mutates the package module object. No filesystem state is persisted.

## Dependencies and Integration Points
It depends on generated modules named `workgen` and `workgen_util` being importable from the package directory. It is consumed by workgen runner scripts, `wtperf.py` generated programs, and benchmark examples that import `Context`, `Table`, `Operation`, and other SWIG-visible names.

## Risks and Edge Cases
The loop `for module in workgen:` assumes the imported `workgen` object is iterable or list-like; if SWIG generation changes to a normal module, import will fail. Appending to `sys.path` can alter import resolution for later imports. Wild re-export can overwrite package attributes and makes static analysis weak.

## Test Signals
A minimal `python -c 'import workgen; from workgen import Context, Operation'` from the built tree is the key signal. Tests should run under Python 3 and from a current working directory outside the package to catch path assumptions.
