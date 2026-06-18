# sources/storage-engines/wiredtiger/lang/python/wiredtiger/init.py

## Purpose
This file is installed as `wiredtiger/__init__.py`. It imports the binary `_wiredtiger` extension and SWIG-generated `swig_wiredtiger`, then re-exports wrapper symbols in the package namespace.

## Important APIs, Types, and Functions
`restart_python` restarts the interpreter after environment changes. Import-time logic validates the installed filename, rejects Python 2, appends the package directory to `sys.path`, optionally configures ThreadSanitizer preloading, imports `_wiredtiger` and `swig_wiredtiger`, and copies all wrapper names into the package module.

## Control Flow
If `TESTUTIL_TSAN=1`, the module runs `clang --print-file-name libtsan.so.2` without `LD_PRELOAD`, updates `LD_PRELOAD`, and restarts Python if TSan must be loaded. If already loaded, it removes TSan from `LD_PRELOAD` for subprocess friendliness without restarting. Normal import then exposes SWIG symbols.

## State and Persistence Behavior
The module mutates `sys.path`, `os.environ["LD_PRELOAD"]`, and module attributes, and can replace the process with `os.execl`.

## Dependencies and Integration Points
It depends on `_wiredtiger.so`, `swig_wiredtiger.py`, Python standard modules, and optionally `clang` for TSan discovery. It is coupled to CMake and pip packaging output names.

## Risks and Edge Cases
Import-time restart can surprise embedding environments. TSan discovery assumes Clang and `libtsan.so.2`. Running this source file before it is installed exits. Extending `sys.path` can affect import resolution.

## Test Signals
Import `wiredtiger` from build and installed packages, verify SWIG symbols are present, and exercise TSan and non-TSan branches where practical.
