# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ApiVersion.java.cmake

## Purpose
This CMake-templated Java source defines the generated `ApiVersion` holder used by the Java bindings to advertise the maximum API version supported by the compiled FoundationDB client package.

## Important APIs, Types, And Functions
`ApiVersion` is a public class with a single public constant, `LATEST`, substituted from `@FDB_AV_LATEST_BINDINGS_VERSION@` during the build. `FDB.selectAPIVersion(int)` uses this value to reject application requests for newer binding behavior than this jar/native library combination supports.

## Control Flow
There is no runtime control flow beyond class loading. Build flow replaces the CMake token before Java compilation; runtime API selection reads the constant when validating the requested API version.

## State And Persistence Behavior
The only state is an immutable class constant baked into the compiled class. It is not persisted separately and does not change for the lifetime of a loaded jar.

## Dependencies And Integration Points
It depends on the FoundationDB build system for substitution and integrates directly with `FDB.selectAPIVersion`. It is part of the Java public API surface, so downstream applications may also compare their compatibility gates against it.

## Risks And Edge Cases
Incorrect substitution can make the Java binding accept or reject the wrong API version. Because the constant is compiled into client code, mixing jars and native libraries from different builds can produce confusing compatibility failures.

## Test Signals
Build tests should assert the generated source contains a numeric `LATEST` value. Runtime tests should cover selecting the latest version, rejecting values above latest, and rejecting versions below the binding minimum.
