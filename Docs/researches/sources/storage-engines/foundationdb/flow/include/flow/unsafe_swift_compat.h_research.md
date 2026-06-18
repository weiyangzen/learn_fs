# sources/storage-engines/foundationdb/flow/include/flow/unsafe_swift_compat.h

## Purpose
This header defines a single unsafe Swift C++ interop annotation for importing C++ types as immortal Swift reference types. It is used where regular ownership cannot yet be represented safely across the Swift/C++ boundary.

## Important APIs, Types, and Functions
The only public API is `UNSAFE_SWIFT_CXX_IMMORTAL_REF`, which expands to Swift attributes `import_reference`, `retain:immortal`, and `release:immortal`. There are no functions or runtime types.

## Control Flow
There is no runtime control flow. The preprocessor guard defines the macro once, and Swift's importer consumes the attributes when compiling with a compiler that understands `swift_attr`.

## State and Persistence Behavior
No state is stored. The macro changes compile-time ownership semantics: Swift treats annotated C++ objects as references that are never retained or released.

## Dependencies and Integration Points
The macro is used by Swift bridge types such as `SwiftContinuationSingleCallbackCInt` in `swift_stream_support.h`. It complements the safer annotation set in `swift_support.h` but is intentionally separated and named unsafe.

## Risks
The file's own warning is the central risk: incorrect use can cause use-after-free or memory leaks. Because Swift will not manage lifetime, the C++ side must guarantee the object outlives all Swift references or intentionally leak it. There is no non-Swift fallback branch, so compilers that do not accept `swift_attr` must still tolerate the attribute syntax.

## Test Signals
Swift import tests should confirm annotated types appear as references with immortal retain/release behavior. Runtime tests for each annotated type should prove the C++ object outlives Swift use and document any intentional leaks. Static review should be required for every new use of the macro.
