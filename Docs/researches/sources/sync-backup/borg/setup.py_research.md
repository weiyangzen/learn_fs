# sources/sync-backup/borg/setup.py

## Purpose
This is BorgBackup's build-time setup entry for extension compilation. Project metadata largely lives in `pyproject.toml`; this file focuses on Cython/C extension discovery, platform-specific extension selection, Cython source generation, long description extraction, and passing build configuration into `setuptools.setup()`.

## Important APIs, Types, and Functions
- Top-level source path constants name Cython modules for compression, crypto, chunkers, hash index, item handling, and platform-specific system calls.
- `cython_sources` lists all `.pyx` files that may need generated C files for source distributions.
- `Sdist` is either the normal setuptools `sdist` command or a guard class that raises if Cython is unavailable when an sdist is requested from a Git checkout lacking generated C files.
- `members_appended(*ds)` merges extension keyword dictionaries by appending list-valued members.
- `lib_ext_kwargs(pc, prefix_env_var, lib_name, lib_pkg_name, pc_version, lib_subdir="lib")` discovers headers/libs from an explicit `BORG_*_PREFIX` environment variable, then from `pkgconfig`, otherwise raises a build error.
- `long_desc_from_readme()` reads `README.rst`, trims content before "What is BorgBackup?", removes badges and unsupported directives, and returns the package long description.
- `setup(cmdclass=..., ext_modules=..., long_description=...)` hands the resulting extension list to setuptools.

## Control Flow
At import time the script attempts to import Cython, records platform flags, builds warning flags, and validates whether generated `.c` files are available if Cython is missing. Unless building on ReadTheDocs, it imports `pkgconfig` when available, discovers OpenSSL/libcrypto, lz4, and platform libraries, constructs extension objects, chooses POSIX/Windows/Linux/BSD/macOS modules by `sys.platform`, and conditionally runs `cythonize` when the command is not `clean`, `egg_info`, help, or version-only. Cythonization first generates C for all platform-specific modules for sdist completeness, then cythonizes extensions for the current platform.

## State and Persistence Behavior
Build execution may generate or update C files from `.pyx` sources and produce compiled extension artifacts in build directories. Environment variables such as `READTHEDOCS`, `BORG_OPENSSL_PREFIX`, `BORG_OPENSSL_NAME`, `BORG_LIBLZ4_PREFIX`, and `BORG_LIBACL_PREFIX` control discovery and whether extensions are built. There is no runtime Borg state, but packaging outputs and generated C files affect reproducibility and installability.

## Dependencies and Integration Points
The file depends on setuptools, optional Cython, optional `pkgconfig`, multiprocessing, compiler toolchains, OpenSSL/libcrypto, liblz4, libacl on Linux, and platform-specific headers. It integrates with `pyproject.toml`, generated Borg Cython modules, ReadTheDocs builds, source distribution generation, and downstream packagers that use `SETUPTOOLS_SCM_PRETEND_VERSION` or library prefix variables.

## Risks and Edge Cases
- Most logic runs at import time, so build failures surface early and can be hard to customize.
- Missing `pkgconfig` is tolerated only until library discovery is needed; users then need explicit prefix variables.
- OpenBSD links a static OpenSSL archive from a versioned path/name, which can break when ports update naming.
- The condition deciding when to cythonize is based on `sys.argv[1]`; unusual chained build commands can skip or trigger Cython unexpectedly.
- Long description extraction asserts a specific README heading and can fail if README structure changes.

## Test Signals
Important coverage includes source builds with and without Cython, sdist generation, installs from sdist without Cython, platform matrix builds for Linux/macOS/Windows/BSD/OpenBSD, and prefix-variable discovery for OpenSSL/lz4/acl. Packaging CI should validate `python -m build`, `pip install .`, import of all compiled modules, and ReadTheDocs mode.
