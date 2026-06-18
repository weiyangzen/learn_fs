# sources/storage-engines/foundationdb/documentation/CMakeLists.txt

## Purpose
This CMake file wires FoundationDB documentation targets into the build. It adds tutorial subdirectories, locates or bootstraps Sphinx, defines reusable documentation generation, serves local previews, and packages generated HTML into the project package set.

## Important APIs, Types, And Functions
`add_documentation_target` is the key CMake function. It accepts `GENERATOR`, optional `DOCTREE`, and optional `ADDITIONAL_ARGUMENTS`, computes an output directory and stamp file, globs Sphinx document files with `CONFIGURE_DEPENDS`, runs `sphinx-build` with `-W`, version/release defines, and creates a custom target named for the generator. Top-level targets include `html`, `docpreview`, and `package_html`.

## Control Flow
CMake first adds `tutorial` and `coro_tutorial`. It finds Python, then Sphinx. If Sphinx is missing, it creates a virtual environment under the build directory, runs `ensurepip`, installs `documentation/sphinx/requirements.txt`, sets `Sphinx_ROOT`, and retries `find_package(Sphinx REQUIRED)`. It then adds the HTML documentation target, chooses a preview server port from `DOCSERVER_PORT` or a stable username hash in the 8000-15999 range, and creates packaging dependencies from `packages` to `package_html` to `html`.

## State And Persistence
Build outputs are under the current binary directory: `sphinx-venv`, generator output directories, doctree cache, stamp files, preview-served HTML, and `${CMAKE_BINARY_DIR}/packages/*-docs-*.tar.gz`. Source files are not modified.

## Dependencies And Integration Points
Dependencies include CMake Python3 support, the repository `FindSphinx` module/package, Sphinx requirements, `FDB_VERSION`, the global `packages` target, and the documentation source tree at `documentation/sphinx`. It integrates with tutorial/coro tutorial builds via subdirectories.

## Risks
The function parses `ADDITIONAL_ARGUMENTS` but does not pass them to the Sphinx command. `message(ERROR ...)` is likely intended to be fatal but CMake fatal errors normally use `message(FATAL_ERROR ...)`. The virtualenv bootstrap performs network/package installation during configure/build if Sphinx is absent. The docs command uses `-W`, so warnings break builds, which is good for quality but brittle during doc changes.

## Test Signals
Signals are CMake configure success with and without a system Sphinx, `cmake --build . --target html`, `docpreview` binding to the expected port, and `package_html` producing the tarball under `packages`.
