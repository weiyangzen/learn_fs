# sources/storage-engines/foundationdb/bindings/python/fdb/apiversion.py.cmake

Purpose: CMake template for the generated Python module containing binding API and package versions.

Important APIs and flow: emits `LATEST_API_VERSION = @FDB_AV_LATEST_BINDINGS_VERSION@` and `FDB_VERSION = "@FDB_VERSION@"`; CMake `configure_file` substitutes these placeholders during the Python binding build.

State and persistence: generated output becomes `fdb/apiversion.py` in the build tree and is imported by `fdb.__init__`. Dependencies are CMake variables loaded from `FDB_API_VERSION_FILE` and project version configuration. Risks include missing or stale substitutions causing import/version selection failures. Test signal is successful package import and `api_version` bound checks.
