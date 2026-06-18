<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_werror.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_werror.py

## Purpose

`gen_werror.py` generates WERROR constants, DOS error name switch cases, friendly message switch cases, and Python bindings from MS-ERREF-style input.

## Important APIs, Types, and Functions

Functions include `generateHeaderFile()`, `generateSourceFile()`, `generateFriendlySourceFile()`, `generatePythonFile()`, `transformErrorName()`, and `main()`.

## Control Flow

`main()` requires input plus four output paths. It parses UTF-8 error data with Windows-error mode enabled, writes `WERR_*` macro definitions, writes C switch cases for symbolic and friendly strings, and writes a Python module initializer exporting numeric WERROR values.

## State and Persistence Behavior

It writes four generated files and stores no runtime state. Generated switch fragments are intended to be included in larger C functions.

## Dependencies and Integration Points

It imports `gen_error_common`, generates code for Samba WERROR handling, and uses Python C API helpers in generated module code.

## Risks and Edge Cases

`WERR_NERR_SUCCESS` is skipped in source switch generation. The usage string mentions fewer outputs than the code requires. Input parsing is format-sensitive.

## Test Signals

Tests should generate from fixture errors, compile generated fragments in their include context, import Python constants, validate `ERROR_` and `WERR_` name normalization, and check friendly messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_werror.py -->
