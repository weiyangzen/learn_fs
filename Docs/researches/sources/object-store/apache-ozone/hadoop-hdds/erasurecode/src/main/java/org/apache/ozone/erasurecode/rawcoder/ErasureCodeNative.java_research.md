<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ErasureCodeNative.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ErasureCodeNative.java

## Purpose
`ErasureCodeNative` centralizes native erasure-code library availability checks, currently relying on Hadoop native code and ISA-L native entry points.

## Important APIs, Types, and Functions
It owns static `LOADING_FAILURE_REASON`, evaluates native loading in a static initializer, and exposes `isNativeCodeLoaded()`, `checkNativeCodeLoaded()`, native `loadLibrary()`, native `getLibraryName()`, and `getLoadingFailureReason()`.

## Control Flow
On class initialization, it checks `NativeCodeLoader.isNativeCodeLoaded()`. If Hadoop native code is available, it calls native `loadLibrary()` and records either `null` or the thrown error string. `checkNativeCodeLoaded` throws `RuntimeException` when loading failed.

## State and Persistence Behavior
Native availability is captured once per JVM in a static final string. There is no retry path or external persistence.

## Dependencies and Integration Points
It depends on Hadoop `NativeCodeLoader`, native JNI methods, and native coder tests that skip with JUnit assumptions when native code is unavailable.

## Risks and Test Signals
Risks include stale one-time failure state, native linkage errors, and relying on Hadoop native libraries before Ozone owns native EC bits. Test signals include native-present and native-absent test environments, assertion of failure reason text, and native coder construction/fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ErasureCodeNative.java -->
