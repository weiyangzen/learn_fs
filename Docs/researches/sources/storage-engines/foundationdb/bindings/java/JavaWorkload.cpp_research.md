# sources/storage-engines/foundationdb/bindings/java/JavaWorkload.cpp

## Purpose
`JavaWorkload.cpp` implements the C++ simulation workload factory used to run Java workloads inside FoundationDB's workload framework. It creates and owns a JVM, injects Java test workload classes into the class path, registers native methods expected by `com.apple.foundationdb.testing.*`, and adapts the C++ `FDBWorkload` lifecycle (`init`, `setup`, `start`, `check`, `getMetrics`) to Java `AbstractWorkload` methods.

## Important APIs, Types, and Functions
- `workloadFactory(FDBLogger*)` exports the FoundationDB workload factory symbol and returns a static `JavaWorkloadFactory`.
- `JavaWorkloadFactory` caches a weak `JVM` instance so workloads in one process share a JVM while allowing cleanup when no workload remains.
- `JVM` wraps `JavaVM*`, `JNIEnv*`, class path tracking, native method registration, class/method/field lookup helpers, and Java object construction.
- Native callbacks registered into Java include `AbstractWorkload.log`, `WorkloadContext` getters/setters/options, and `Promise.send`.
- `JavaPromise` owns a moved `GenericPromise<bool>` and deletes itself after `send`, making the Java promise object a native pointer holder.
- `JavaWorkload` stores the Java workload global reference, the converted class name, the workload context, and a failure flag.

## Control Flow
The factory creates a `JavaWorkload`, replacing dots in the requested workload name with slash-separated JNI class names. `JavaWorkload::init` reads the `classPath` workload option, splits it on `;` and `,`, adds each path through `URLClassLoader.addURL`, initializes native registrations once, creates a Java `WorkloadContext`, and instantiates the requested workload class. Lifecycle calls allocate a Java `FDBDatabase` wrapper around the native `FDBDatabase*`, allocate a Java `Promise`, call `setup`, `start`, or `check`, then let Java asynchronously call back into `Promise.send`. `getMetrics` calls Java `getMetrics`, iterates the returned `List<PerfMetric>`, reads fields, and pushes `FDBPerfMetric` values back to C++.

## State and Persistence Behavior
Persistent state is process-local and native: the JVM, cached class path set, static Java logger pointer, global Java workload reference, and pending `JavaPromise` objects. Database state is not persisted here; database pointers are passed through to Java wrappers. The code mutates the Java system class loader and globally registers native methods, so JVM state is effectively singleton-like for the process. `JavaWorkload` uses `failed` to short-circuit later lifecycle calls after JNI setup or invocation failures.

## Dependencies and Integration Points
This file depends on `foundationdb/CppWorkload.h`, the FDB C API, JNI, generated JNI headers for testing classes, Boost string splitting/replacement, and Java classes under `com.apple.foundationdb.testing` and `com.apple.foundationdb`. It integrates with Java bindings by selecting `FDB_API_VERSION`, disabling the Java shutdown hook, constructing `FDBDatabase`, and using workload-provided executors.

## Risks and Edge Cases
JNI local reference management is partial; many local references from map iteration, class lookup, and metric iteration are not explicitly deleted, so long-running or high-cardinality workloads could stress local reference tables. `createWorkload` calls `NewGlobalRef(res)` but ignores the return value, leaving `workload` as the original local reference; if this runs beyond the local frame lifetime, that is a correctness risk. `JVM::addToClassPath` assumes the system class loader supports `URLClassLoader.addURL`, which is not true for newer Java module-era class loader implementations unless the environment arranges compatibility. `JavaPromise` deletes itself on `send`; double-send from Java would be use-after-free. Errors during `setup/start/check` set `failed` but do not always complete the C++ promise, which can hang callers if an exception occurs after the native promise was handed off.

## Test Signals
The file is exercised indirectly by simulation workloads that load Java workload classes and by Java binding tests that require the JNI library to be functional. Good test signals include workload lifecycle completion, Java-side logging through native logger pointers, option reads from `WorkloadContext`, and metric extraction. There are no direct unit tests in this subset for the global-reference lifetime or class-loader assumptions.
