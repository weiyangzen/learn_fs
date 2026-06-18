# File Research: sources/virtualization/libblockdev/src/lib/plugin_apis/Makefile.am

## Role
Automake rules for generating core-library plugin API wrapper C/H files from `.api` specifications.

## Build Logic
- `API_FILES` discovers all `*.api` files in this directory.
- `SOURCE_FILES` and `HEADER_FILES` are derived by replacing `.api` with `.c` and `.h`.
- `all-local` depends on `generate_boilerplate`.
- Pattern rule invokes `scripts/boilerplate_generator.py` with `${PYTHON}` to generate files into the build directory.
- Generated and source API files are included in `dist_noinst_HEADERS`.
- Generated C/H outputs are removed via `CLEANFILES`.

## Dependencies and Interactions
- `blockdev.c.in` includes generated `plugin_apis/*.h` and `plugin_apis/*.c` directly.
- `src/lib/Makefile.am` includes generated headers in introspection scans.

## Filesystem/Storage Relevance
This file creates the dynamic dispatch wrappers that let the central library expose plugin APIs without statically linking plugin implementations.
