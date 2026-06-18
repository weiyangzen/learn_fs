# File Research: sources/virtualization/nbdkit/plugins/python/errors.c

## Purpose
Converts Python exceptions raised by plugin callbacks into nbdkit error messages, preferably with full Python traceback text.

## Main Entry Points
- `check_python_failure()` detects a pending Python exception, fetches and normalizes it, tries to print a formatted traceback, and returns `-1`.
- `print_python_traceback()` imports Python’s `traceback` module and calls `format_exception`.
- `print_python_error()` falls back to stringifying the exception object.

## Dependencies
Uses Python C API, nbdkit error logging, `python_to_string()`, and global `script` from the Python plugin adapter.

## Risks and Notes
Several temporary Python objects from error handling are not decref’d on all paths, so repeated callback exceptions may leak Python references. Traceback formatting itself can fail, in which case the fallback only prints the exception string.
