# sources/storage-engines/wiredtiger/lang/python/setup_pip.py

## Purpose
This setuptools script builds and packages the WiredTiger Python module for `pip`, including a CMake/Ninja WiredTiger build and the SWIG-generated Python extension.

## Important APIs, Types, and Functions
Helpers include `msg`, `die`, `build_commands`, `get_compile_flags`, `get_sources_curdir`, `get_wiredtiger_versions`, and `get_library_dirs`. `BinaryDistribution` marks the package as non-pure. `WTBuildExt` runs CMake and Ninja once, guarded by `built.txt`, before building the extension. `WTInstall` runs `build_ext` and moves generated `wiredtiger.py` to `wiredtiger/swig_wiredtiger.py`.

## Control Flow
The script locates the WiredTiger root, rejects 32-bit Python and Windows, reads `RELEASE_INFO`, configures a static PIC Python-enabled CMake build, and computes flags. For `sdist`, it requires Python 3, stages tracked Git files, copies package Python files to the stage root, renames `init.py` to `__init__.py`, and writes dist output. For normal build/install, `build_ext` runs configure/build commands before setuptools compiles `_wiredtiger`.

## State and Persistence Behavior
It creates `cmake_pip_build`, `built.txt`, source staging, and dist artifacts. It changes working directories and removes staging after `sdist`.

## Dependencies and Integration Points
It depends on setuptools, CMake, Ninja, Git, SWIG-generated sources, `RELEASE_INFO`, `README`, and POSIX shell commands. It installs `_wiredtiger` under the `wiredtiger` package and uses `swig_wiredtiger.py` for wrapper symbols.

## Risks and Edge Cases
Commands run through `sh -c`; Windows is unsupported. `get_wiredtiger_versions` uses `exec` on trusted release assignments. `sdist` requires Git and can stage many files. The build sentinel can hide changed configuration unless cleaned.

## Test Signals
Run `python setup_pip.py sdist`, install from the generated distribution, import `wiredtiger`, and verify generated wrapper placement.
