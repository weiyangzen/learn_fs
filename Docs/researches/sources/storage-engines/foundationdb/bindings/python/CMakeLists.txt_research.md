# sources/storage-engines/foundationdb/bindings/python/CMakeLists.txt

Purpose: CMake packaging pipeline for the pure-Python FoundationDB binding.

Important APIs and flow: `SRCS` lists Python sources, metadata, README, manifest, and platform-specific `.pth` library pointer files. A copy loop mirrors sources into the build tree and creates `python_binding`. `vexillographer_compile` generates `fdboptions.py`; API version data is included from `FDB_API_VERSION_FILE` and configured into `fdb/apiversion.py`. The file optionally adds a `pycodestyle` check, configures release suffixes, creates a venv, installs `build`, and runs `python -m build` to produce sdist and py3-none-any wheel package artifacts.

State and persistence: creates build-tree files, generated option/version modules, virtualenv, dist outputs, and package copies under `${CMAKE_BINARY_DIR}/packages`. Dependencies include CMake, Python3, pip/build, vexillographer, version variables, and platform library path files. Risks include network/tool availability for pip, missing API version definitions, stale source list, and platform-specific `.pth` TODO for Windows. Signal is successful `python_binding`, style target, and package artifacts.
