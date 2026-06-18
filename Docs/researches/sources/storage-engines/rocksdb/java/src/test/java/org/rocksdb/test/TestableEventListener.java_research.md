# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/TestableEventListener.java

Purpose: Test-only `AbstractEventListener` subclass that exposes a native hook to invoke all enabled event callbacks.

Important APIs/types/functions: constructors forwarding optional `EnabledEventCallback...`, `invokeAllCallbacks()`, and native `invokeAllCallbacks(long handle)`.

Control flow and state: construction delegates enabled callback configuration to `AbstractEventListener`. `invokeAllCallbacks()` passes the listener native handle to JNI, which triggers callback dispatch for tests.

State and persistence behavior: listener state is native-handle backed; no persistence. Correctness depends on the listener remaining open while native callbacks execute.

Dependencies and integration points: integrates RocksJava event listener JNI and tests that need deterministic callback invocation without requiring real compaction/flush/table events.

Risks: native method availability and handle lifetime are critical; misuse after close can hit invalid native state. Callback coverage depends on JNI implementation, not visible in this Java file.

Test signals: helper for event listener tests; downstream assertions validate callback observability.
