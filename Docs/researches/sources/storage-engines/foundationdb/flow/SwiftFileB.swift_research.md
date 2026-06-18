<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SwiftFileB.swift -->
# sources/storage-engines/foundationdb/flow/SwiftFileB.swift
- Purpose: Tiny Swift/C++ interop compilation probe.
- Important APIs/types/functions: Exposes `swiftFileB()` to C++ with `@_expose(Cxx)`.
- Control flow: Function body is empty; its value is in compile/link visibility rather than runtime behavior.
- State and persistence behavior: No state and no persistence.
- Dependencies and integration points: Imports `Flow` and depends on Swift C++ interop support. It likely participates in build-system validation that multiple Swift files can expose symbols.
- Risks: `@_expose(Cxx)` is underscored Swift functionality, so compiler-version compatibility matters. Runtime risk is negligible.
- Test signals: Successful build and C++ linkage against `swiftFileB` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SwiftFileB.swift -->
