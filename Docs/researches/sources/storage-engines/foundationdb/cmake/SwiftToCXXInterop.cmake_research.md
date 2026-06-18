# sources/storage-engines/foundationdb/cmake/SwiftToCXXInterop.cmake

## Purpose
Creates custom targets that emit C++ headers for Swift modules using Swift's reverse C++ interoperability.

## Important APIs, Types, and Functions
Defines `add_swift_to_cxx_header_gen_target(target_name header_target_name header_path SOURCES ... FLAGS ...)`.

## Control Flow and Integration
The function verifies Swift reverse interop support/version, resolves Swift sources, extracts selected flags from `CMAKE_Swift_FLAGS`, then runs `swiftc -frontend -typecheck -emit-clang-header-path` with target include dirs and frontend options.

## State and Persistence
Depends on Swift toolchain `experimental-interoperability-version.json`, Swift compiler frontend, target include properties, and `FindSwiftLibs`/`CompilerChecks` includes.

## Dependencies
Generated C++ header persists at `header_path` and is represented by `header_target_name`.

## Risks and Test Signals
Risks include regex flag extraction missing quoted/complex flags, toolchain version gating, and header generation not tracking all transitive module dependencies. Test signal is generated header and successful C++ compilation against Swift APIs.
