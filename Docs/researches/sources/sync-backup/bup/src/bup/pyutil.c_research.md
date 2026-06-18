## sources/sync-backup/bup/src/bup/pyutil.c

Purpose: C extension utility functions for safe allocation and Python integer conversion.

Important APIs and control flow: `checked_calloc()` returns `calloc()` memory or sets `PyErr_NoMemory()`. `checked_malloc(n, size)` uses `INT_MULTIPLY_OK` to reject allocation-size overflow, then mallocs or raises memory errors. `bup_ulong_from_py()`, `bup_uint_from_py()`, and `bup_ullong_from_py()` validate `PyLong` inputs, call Python unsigned conversion APIs, and replace generic overflow messages with argument-specific diagnostics.

State and dependencies: no persistent state; depends on Python C API, generated config, `pyutil.h`, and `intprops.h`.

Risks and tests: callers must check NULL/zero returns and propagate Python exceptions. Unsigned conversions reject negative Python ints through Python’s conversion APIs. Coverage is indirect through C helpers such as `_helpers` and any tests exercising large numeric inputs.
