## sources/sync-backup/bup/src/bup/compat.c

Purpose: compatibility implementation for invoking Python with byte argv on Python 3.7.

Important APIs and control flow: when Python is older than 3.8, `bup_py_bytes_main(argc, argv)` allocates a wide argv array with `PyMem_RawMalloc`, decodes each byte argv using `Py_DecodeLocale`, reports decode/allocation errors with `die()`, and calls `Py_Main()`.

State and dependencies: transient allocation only; depends on Python C API, `bup.h`, `bup/io.h`, and compile-time Python version checks. For Python 3.8+, `bup.c` uses `Py_BytesMain` instead.

Risks and tests: decoded wide strings are not freed before `Py_Main()` exits, which is acceptable for process lifetime. Error paths must avoid returning with a Python exception only. Launcher behavior is covered indirectly by installed and development command tests.
