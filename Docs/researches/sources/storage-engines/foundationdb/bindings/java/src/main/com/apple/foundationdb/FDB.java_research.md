# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDB.java

## Purpose
`FDB` is the Java binding entry point and singleton owner for API-version selection, native library loading, network lifecycle, database opening, global network options, direct-buffer configuration, and error predicate access.

## Important APIs, Types, And Functions
Important public APIs include `selectAPIVersion`, `instance`, `options`, `open` overloads, deprecated `createCluster` overloads, `startNetwork`, `stopNetwork`, `disableShutdownHook`, `setUnclosedWarning`, `enableDirectBufferQuery`, and `resizeDirectBufferPool`. Native methods bridge API selection, network setup/run/stop, option setting, error predicates, and database creation.

## Control Flow
Static initialization tries to load `fdb_c`, then loads `fdb_java`, and creates a daemon callback executor. `selectAPIVersion` validates the requested version, calls native `Select_API_version`, and installs the singleton. `open` synchronizes network startup, creates a native database pointer, and wraps it in `FDBDatabase`. `startNetwork` configures native networking, installs an optional shutdown hook, and runs `Network_run` on a supplied executor. `stopNetwork` calls `Network_stop` and waits on a semaphore until the network thread exits.

## State And Persistence Behavior
The singleton and selected API version are JVM-global and immutable after selection. Network lifecycle flags prevent restart after stop. Direct-buffer query preference and warning preference are mutable instance settings. No persistent files are written by `FDB` itself.

## Dependencies And Integration Points
It depends on `JNIUtil`, generated `ApiVersion`, `NetworkOptions`, `Database`, `FDBDatabase`, `Cluster`, `DirectBufferPool`, and the native FoundationDB JNI library. Most other binding classes reach `FDB.instance()` for defaults, warnings, or direct-buffer flags.

## Risks And Edge Cases
API version can be selected only once. `stopNetwork` is terminal. Shutdown hook ordering can race application hooks unless disabled. Native library load failures surface during class initialization. `startNetwork` swallows network-thread errors after printing to stderr.

## Test Signals
Tests should cover API-version bounds, singleton repeat selection, network start idempotence, stop terminal behavior, database open with default/custom executor and event keeper, shutdown-hook disable, direct-buffer toggles, and native-load failure paths in integration packaging tests.
