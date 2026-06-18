# sources/sync-backup/bup/dev/python.c

## Purpose
C wrapper executable for launching Python with bup's configured embedded Python flags.

## Important APIs, Types, and Functions
Includes generated `config/config.h`, Python headers, and `bup/compat.h`. Defines `bup_py_main` as `bup_py_bytes_main` before Python 3.8 or `Py_BytesMain` otherwise.

## Control Flow
`main` asserts `argc > 0` and delegates all args to the selected Python bytes-aware main function.

## State and Persistence Behavior
No persistence. Runtime behavior is process execution of Python.

## Dependencies and Integration Points
Built by `GNUmakefile` into `dev/python`; validated by `dev/validate-python`; used by scripts needing the configured Python runtime.

## Risks and Test Signals
Risks include Python C API version differences and config/header mismatch. Signals are successful compile/link and version validation.
