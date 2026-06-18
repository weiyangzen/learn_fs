# sources/storage-engines/foundationdb/flow/protocolversion/protocol_version.py

## Purpose
This Python tool reads FoundationDB protocol-version definitions from a CMake-style source file and generates language-specific protocol-version code for C++, Java, or Python. It centralizes version constants and feature gates so multiple language bindings stay aligned with the same `FDB_PV_*` input definitions.

## Important APIs, Types, And Functions
`ProtocolVersion` stores default, future, minimum compatible, minimum invalid, left-most-check, least-significant-bit mask, and a mapping from version integer to feature names. `CMakeProtocolVersionSerializer` loads `set(FDB_PV_* "0x...LL")` definitions and dispatches special fields through `SPECIAL_FIELDS`. `NameTransformer` has Java camel-case, C++ camel-case with compatibility mappings, and snake/lowercase implementations. `JavaCodeGen`, `CxxHeaderFileCodeGen`, and `PythonLibraryCodeGen` render Jinja templates from `SCRIPT_DIRECTORY`. `_setup_args` defines `--source`, `--generator`, and `--output`; `main` wires source loading, generator selection, and output writing.

## Control Flow
The CLI parses arguments, opens the source file, loads all matching CMake `set(...)` lines, converts hex strings to integers, stores recognized special fields, and treats all other `FDB_PV_*` symbols as feature flags keyed by version. It selects the generator based on `cpp`, `java`, or `python`, builds a Jinja environment with filters for version encoding and feature-name transformation, renders the appropriate template, and writes the output file.

## State And Persistence
All state is in memory until the generated output file is written. Feature ordering follows insertion order in Python dictionaries and source-file scan order within each feature list. There is no cache or persistent metadata. The generated files become the durable output consumed by the build or bindings.

## Dependencies And Integration Points
The script depends on Python 3, `argparse`, `json`, `re`, `jinja2`, and the sibling templates `ProtocolVersion.h.template`, `ProtocolVersion.java.template`, and `protocol_version.py.template`. It integrates with FoundationDB build rules that generate protocol-version code from CMake definitions for Flow/C++ and language bindings.

## Risks
The JSON serializer class is misspelled as `JSONProtocolVersionSerialzer` and calls `json.dumps(..., ident=2)`, which would fail if that unused serializer path were exercised. `_min_compatibile_version` is misspelled internally but consistently exposed through the property, so it is harmless unless external reflection expects the correct spelling. The CMake parser handles only a narrow quoted `set(NAME "VALUE")` form and silently skips nonmatching lines. Feature ordering is not explicitly sorted, so template output stability depends on source ordering. `jinja2.Environment(autoescape=True)` is unusual for code generation and can escape data if templates include characters subject to autoescaping.

## Test Signals
Useful tests load a representative protocol CMake file and compare generated C++/Java/Python files to checked-in goldens. Name-transform tests should cover special mappings such as `IPV6`, `TSS`, `DR_BACKUP_RANGES`, and `PROCESS_ID`. CLI tests should verify unknown generator failure, missing arguments, malformed CMake lines, and exact hex encoding suffixes for each language.
