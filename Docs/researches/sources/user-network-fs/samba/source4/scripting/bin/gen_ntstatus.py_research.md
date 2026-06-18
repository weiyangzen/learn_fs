<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_ntstatus.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_ntstatus.py

## Purpose

`gen_ntstatus.py` generates NTSTATUS constants, C name/description tables, Python bindings, and Rust constants from MS-ERREF-style input.

## Important APIs, Types, and Functions

Functions include `generateHeaderFile()`, `generateSourceFile()`, `generatePythonFile()`, `generateRustFile()`, `transformErrorName()`, and `main()`. It also constructs a synthetic `NT_STATUS_OK` entry.

## Control Flow

`main()` expects input, header, source, Python, and Rust output paths. It parses UTF-8 input through `parseErrorDescriptions()`, inserts `NT_STATUS_OK` at the front, and writes all outputs. Name transformation normalizes `STATUS_`, `RPC_NT_`, and `EPT_NT_` prefixes.

## State and Persistence Behavior

It writes four generated files. Generated C defines static error-name and description arrays; generated Rust defines a tuple struct, constants, descriptions, and formatting traits.

## Dependencies and Integration Points

It imports `ErrorDef` and parser helpers from `gen_error_common`, generates code consumed by Samba's NTSTATUS utilities and Python modules, and participates in Rust bindings.

## Risks and Edge Cases

The Rust generator skips descriptions for a few duplicated/special constants to avoid pattern conflicts. Parser assumptions mirror the common helper. Generated arrays rely on downstream sentinel handling.

## Test Signals

Tests should compile generated C and Rust from fixtures, import Python constants, verify prefix normalization, ensure `NT_STATUS_OK` ordering, and validate description omission behavior for special constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_ntstatus.py -->
