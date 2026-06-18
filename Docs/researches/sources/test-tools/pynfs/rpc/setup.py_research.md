<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/setup.py -->
# sources/test-tools/pynfs/rpc/setup.py

Purpose: packaging entry point for the `rpc` Python package in pynfs, with a custom `build_py` command that compiles local XDR `.x` specifications into Python modules before regular package module discovery.

Important APIs and functions: `build_py.build_packages()` mirrors setuptools' package loop, calls `check_package`, then `expand_xdr`, then `find_package_modules` and `build_module`. `build_py.expand_xdr(dir)` changes into the package directory, glob-scans `*.x`, and calls `xdrgen.run(f)`. The final `setup(...)` registers package metadata and `cmdclass={"build_py": build_py}`.

Control flow: import `xdrgen` normally, falling back to `use_local` path injection if unavailable. During build, each package directory is scanned and generated code is produced before modules are copied into the build tree.

State and persistence: writes are delegated to `xdrgen.run`, which creates generated `_const.py`, `_type.py`, and `_pack.py` siblings for each `.x` file in the current working directory. The function temporarily mutates process cwd and restores it in `finally`.

Dependencies and integration: depends on setuptools, `glob`, `os`, local `xdrgen`, and pynfs' source layout. It integrates with Python packaging and the XDR generator under `sources/test-tools/pynfs/xdr`.

Risks: `glob(os.path.join(dir, "*.x"))` is evaluated after `chdir(dir)`, so non-empty relative `dir` can become double-relative. `os.chdir` makes the command process-global and fragile under concurrent builds. The version is a placeholder and dependency declarations are absent. Test signals are build-time: run `python setup.py build` from `rpc`, confirm generated files exist, and verify no cwd leak on failure.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/setup.py -->
