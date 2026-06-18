# sources/storage-engines/foundationdb/cmake/FindSphinx.cmake

## Purpose
Discovers the `sphinx-build` executable for documentation builds.

## Important APIs, Types, and Functions
Sets `Sphinx_EXECUTABLE`, parses `Sphinx_VERSION` from `sphinx-build --version`, and reports `Sphinx_FOUND`.

## Control Flow and Integration
Documentation-related CMake can require or use this module when `WITH_DOCUMENTATION` is enabled.

## State and Persistence
Depends on `Sphinx_ROOT` or PATH lookup and the executable's version output format.

## Dependencies
No persistence beyond CMake variables.

## Risks and Test Signals
Risks include version substring parsing if Sphinx output changes. Test signal is documentation target configure/build success.
