# sources/storage-engines/foundationdb/bindings/CMakeLists.txt

## Purpose
This CMake file coordinates optional language binding subdirectories and bindingtester packaging.

## Important APIs, Types, And Functions
It always adds `c`, conditionally adds `flow` when not `OPEN_FOR_IDE`, and gates `python`, `java`, `go`, `ruby`, and `swift` subdirectories on corresponding `WITH_*_BINDING` options. On non-Windows non-IDE builds it calls `package_bindingtester()` and `package_bindingtester2()`.

## Control Flow
CMake processes binding subdirectories in a fixed order. Swift binding inclusion also checks that `bindings/swift` exists before adding it.

## State And Persistence Behavior
The file configures build targets and packaging outputs; it does not directly write runtime data.

## Dependencies And Integration Points
It integrates top-level component options with language binding build systems and binding tester packaging functions defined elsewhere.

## Risks And Edge Cases
Flow and Go bindings are skipped for IDE-only configuration. Swift can be enabled but skipped if sources are absent, with only a status message. Bindingtester packaging is disabled on Windows.

## Test Signals
CMake configure/build target presence and packaged bindingtester artifacts are the main signals.
