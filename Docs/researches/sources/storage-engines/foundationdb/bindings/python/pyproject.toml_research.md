# sources/storage-engines/foundationdb/bindings/python/pyproject.toml

Purpose: This file declares packaging metadata for the Python FoundationDB binding using setuptools as the PEP 517 build backend.

Important APIs and types: It defines `setuptools.build_meta`, project name `foundationdb`, dynamic version from `fdb.__version__`, authors, description, keywords, URLs, Python requirement `>=3.8`, classifiers, and package discovery restricted to `fdb`.

Control flow: Build tools read the metadata, import `fdb.__version__` for the dynamic version, and find only the `fdb` package to avoid accidental modules in CMake build directories.

State and persistence behavior: It affects generated package metadata and distribution contents, not runtime database state.

Dependencies and integration points: It integrates with pip/build/setuptools and the binding package layout. The comment about restricting package discovery is tied to CMake out-of-source or in-build-tree usage.

Risks: Dynamic version import can execute package import-time code if not carefully isolated by setuptools. The package discovery include list is narrow and must be updated if new top-level Python packages are added.

Test signals: Packaging tests or install builds should confirm that only intended binding modules are included and the version matches `fdb.__version__`.
