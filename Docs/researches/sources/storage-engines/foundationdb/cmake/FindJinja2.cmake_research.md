# sources/storage-engines/foundationdb/cmake/FindJinja2.cmake

## Purpose
Detects the Python Jinja2 templating package for generation workflows.

## Important APIs, Types, and Functions
Finds Python3 interpreter and runs `python -c 'import jinja2; print(jinja2.__version__)'`, producing `Jinja2_VERSION` and `Jinja2_FOUND`.

## Control Flow and Integration
The module uses Python import success as the only discovery path, then delegates result validation to `find_package_handle_standard_args`.

## State and Persistence
Depends on Python3 and an importable `jinja2` package in that interpreter environment.

## Dependencies
No persistence beyond CMake variables.

## Risks and Test Signals
Risks include mismatch between configure Python and build/runtime Python. Test signal is configure-time Jinja2 version detection.
