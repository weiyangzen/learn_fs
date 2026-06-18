<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SwiftBridging.swift -->
# sources/storage-engines/foundationdb/flow/SwiftBridging.swift
- Purpose: Provides small Swift-side convenience wrappers for Flow/C++ bridging.
- Important APIs/types/functions: Public `BUGGIFY(file:line:)` and `pprint(_:file:line:function:)`.
- Control flow: `BUGGIFY` captures Swift call-site defaults, asserts the file static string has a pointer representation, and calls `SwiftBridging.buggify` with the UTF-8 pointer and line. `pprint` formats diagnostic output with Swift file, line, and function.
- State and persistence behavior: No retained state and no persistence. Effects are delegated to Flow buggify logic or stdout logging.
- Dependencies and integration points: Imports the `Flow` Swift module and bridges to generated/exposed C++ symbols. Intended for Swift code participating in Flow simulation/testing diagnostics.
- Risks: The pointer representation assertion can fail for non-pointer `StaticString` values. `pprint` writes directly to stdout, which may bypass Flow trace infrastructure and deterministic logging conventions.
- Test signals: Swift interop tests should verify `BUGGIFY` calls into Flow with correct file/line and that the module builds under supported Swift/C++ interop settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SwiftBridging.swift -->
