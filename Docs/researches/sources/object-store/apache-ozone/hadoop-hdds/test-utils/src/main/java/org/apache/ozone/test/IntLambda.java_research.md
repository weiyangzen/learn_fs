# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/IntLambda.java

Purpose: `IntLambda` provides a small functional helper for tests that execute integer-returning code while supplying text on `System.in`.

Important APIs and types: It defines static method `withTextFromSystemIn(String...)` returning `ToIntExecutable`, and nested functional interface `ToIntExecutable` with `execute(IntSupplier code)`.

Control flow: `withTextFromSystemIn` creates an executable that uses `GenericTestUtils.supplyOnSystemIn` in a try-with-resources block, invokes the supplied `IntSupplier`, returns its integer result, rethrows runtime exceptions, and wraps checked restore failures in `RuntimeException`.

State and persistence behavior: No durable state. It temporarily mutates global `System.in` and relies on the returned `AutoCloseable` to restore it.

Dependencies and integration points: It integrates with CLI-style tests where command handlers read from stdin and return integer status codes. It depends on `GenericTestUtils`.

Risks: Like all global stdin replacement helpers, it is unsafe if used concurrently with other tests reading `System.in`. `IntSupplier` cannot throw checked exceptions directly.

Test signals: Downstream tests can assert integer return codes while providing deterministic stdin content.
