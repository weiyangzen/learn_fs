# File Research: sources/virtualization/nbdkit/plugins/python/helpers.c

## Purpose
Provides small helper functions for the Python plugin adapter.

## Main Entry Points
- `callback_defined()` checks whether the loaded Python module has a callable attribute with the requested callback name.
- `python_to_string()` converts Python Unicode or bytes objects into newly allocated C strings.

## Dependencies
Uses Python C API and globals `script` and `module` from the Python plugin adapter.

## Risks and Notes
`callback_defined()` clears `AttributeError` from missing callbacks, which is expected, and rejects non-callable attributes with a debug message. `python_to_string()` does not check whether `PyUnicode_AsUTF8()` failed before passing the result to `strdup`, so callers must be prepared for NULL returns on conversion failure.
