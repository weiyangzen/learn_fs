# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyOutputStream.java

Purpose: `SpyOutputStream` wraps an `OutputStream` and records close calls so tests can assert output stream lifecycle behavior.

Important APIs and types: It extends `FilterOutputStream`, uses an `AtomicInteger`, overrides `close`, and provides `assertClosedExactlyOnce`.

Control flow: `close` increments the counter and delegates to the wrapped output stream close. The assertion method verifies the counter is one with JUnit.

State and persistence behavior: Runtime-only close count; no persistent state.

Dependencies and integration points: Used by tests that verify writers, serializers, or IO helpers close caller-provided output streams exactly once.

Risks: Repeated close calls are passed through to the underlying stream. Like the input variant, it supports only one specific assertion.

Test signals: Exact one close invocation.
