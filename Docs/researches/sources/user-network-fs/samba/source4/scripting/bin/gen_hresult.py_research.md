<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_hresult.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_hresult.py

## Purpose

`gen_hresult.py` generates HRESULT headers, C lookup code, and Python bindings from MS-ERREF-style input.

## Important APIs, Types, and Functions

Functions include `write_license()`, `generateHeaderFile()`, `generateSourceFile()`, `generatePythonFile()`, `transformErrorName()`, and `main()`. Generated APIs include `HRESULT`, `HRES_ERROR`, `HRES_ERROR_V`, `hresult_errstr_const()`, `hresult_errstr()`, and conversion helpers for Win32-backed HRESULTs.

## Control Flow

`main()` requires four arguments after the script name: input table, header output, C source output, and Python source output. It parses errors with `parseErrorDescriptions()`, writes the header with macros and constants, writes C switch-based name/description lookup, and writes a Python module initializer exporting constants.

## State and Persistence Behavior

It writes three generated files. Generated source contains static lookup data and a static fallback message buffer.

## Dependencies and Integration Points

It imports `gen_error_common`, uses Samba WERROR helpers in generated C, and generates Python C-extension code.

## Risks and Edge Cases

Generation assumes trusted input; strings are escaped only by the common helper. The source lookup has unreachable `break` after `return` in one path but harmless. Missing or malformed arguments exit after usage output.

## Test Signals

Tests should generate from a small fixture, compile generated C, import generated Python module, verify Win32 HRESULT conversion fallback, and check names/descriptions with escaped input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_hresult.py -->
