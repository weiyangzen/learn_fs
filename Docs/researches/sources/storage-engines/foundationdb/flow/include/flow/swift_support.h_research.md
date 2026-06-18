# sources/storage-engines/foundationdb/flow/include/flow/swift_support.h

## Purpose
This header centralizes Swift interop annotations and small declarations for Flow C++ types. It lets the same C++ headers compile in Swift-enabled and non-Swift builds by defining Swift attributes under `WITH_SWIFT` and no-op fallbacks otherwise.

## Important APIs, Types, and Functions
Swift-enabled macros include `SWIFT_CXX_IMMORTAL_SINGLETON_TYPE`, `SWIFT_CXX_REF`, `SWIFT_CXX_IMPORT_UNSAFE`, `SWIFT_CXX_IMPORT_OWNED`, `SWIFT_SENDABLE`, `SWIFT_STRINGIFY`, `CONCAT2`, `CONCAT3`, nullability annotation helpers, and `_Nullable`/`_Nonnull` fallbacks when needed. It declares `TaskPriority swift_priority_to_net2(swift::JobPriority p)`. Non-Swift builds define annotation macros as empty and preserve compatibility macros.

## Control Flow
All behavior is preprocessor-controlled. Under `WITH_SWIFT`, the header includes Swift ABI task definitions and Flow task priority definitions, then defines Clang `swift_attr` annotations. It also detects compiler nullability support and either emits `clang assume_nonnull` pragmas or erases nullability markers. Without Swift, the macros collapse to no-ops.

## State and Persistence Behavior
No runtime state is stored. The important effect is compile-time import metadata consumed by Swift's C++ interop importer. Annotations influence ownership, Sendable conformance, reference importing, and unsafe projection behavior.

## Dependencies and Integration Points
Swift-enabled builds depend on `flow/swift/ABI/Task.h` and `flow/TaskPriority.h`. This file is included by `swift.h` and many C++ types that want to expose Swift import behavior without hard requiring Swift support.

## Risks
Wrong annotations can create memory-management bugs in Swift, especially immortal or reference-retained types. The no-op branch can hide Swift-only assumptions until a Swift build is run. `SWIFT_NAME` is only defined in the non-Swift branch here; if users expect it under `WITH_SWIFT`, they must get it from generated Swift headers or another include. Priority conversion must stay aligned with `swift::JobPriority` values.

## Test Signals
Both Swift and non-Swift builds should compile headers that use these macros. Swift import tests should verify annotated C++ types appear with expected ownership and Sendable behavior. Scheduling tests should validate `swift_priority_to_net2` for every `swift::JobPriority`.
