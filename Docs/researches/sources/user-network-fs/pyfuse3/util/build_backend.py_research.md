# sources/user-network-fs/pyfuse3/util/build_backend.py

Purpose: Custom PEP 517 backend wrapper that configures the pyfuse3 Cython extension dynamically from `pkg-config` and platform detection before delegating to setuptools.

Important APIs/types/functions: Re-exports `setuptools.build_meta` hooks. `pkg_config` validates minimum versions and parses cflags/libs. `get_extension_modules` creates extension `pyfuse3.__init__` from `src/pyfuse3/__init__.pyx`, adds libfuse compile/link flags, appends `-lrt` on Linux/GNU kFreeBSD and `darwin_compat.c` on Darwin. `build_wheel` and `build_editable` monkey-patch `Distribution.__init__` to inject `ext_modules`; `build_sdist` delegates unchanged.

Control flow: Build frontend imports this backend. Wheel/editable builds patch setuptools distribution construction for the duration of the underlying build hook, then restore the original initializer in `finally`.

State and persistence: Temporarily mutates `setuptools.Distribution.__init__` in-process. Build artifacts are produced by setuptools; this file does not persist its own state.

Dependencies and integration points: Depends on `pkg-config`, `fuse3 >= 3.2.0`, Cython, setuptools, pthread, and platform `os.uname`. Tied to `pyproject.toml` build-backend settings.

Risks: Monkey-patching setuptools internals is brittle with future setuptools changes. `pkg_config` reads only one stdout line and assumes ASCII. Cross-compilation may be limited by `os.uname` host detection.

Test signals: Package build success is the primary validation. CI jobs that install/build pyfuse3 exercise this path.
