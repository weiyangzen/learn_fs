# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyInputStream.java

Purpose: `SpyInputStream` wraps an `InputStream` and records how many times it is closed so tests can assert close behavior.

Important APIs and types: It extends `FilterInputStream`, uses an `AtomicInteger` close counter, overrides `close`, and exposes `assertClosedExactlyOnce`.

Control flow: Construction delegates to `FilterInputStream`. Each `close` increments the counter and then closes the wrapped stream. `assertClosedExactlyOnce` asserts the counter equals one through JUnit.

State and persistence behavior: No persistence. Runtime state is the close counter.

Dependencies and integration points: Useful in tests that validate resource ownership and stream lifecycle for APIs receiving or returning input streams.

Risks: It only exposes the exact-once assertion; tests needing zero, at-least, or exact-N closes need another helper. The underlying close is still executed on every call, so repeated close behavior depends on the wrapped stream.

Test signals: JUnit assertion passes only when exactly one close call occurred.
